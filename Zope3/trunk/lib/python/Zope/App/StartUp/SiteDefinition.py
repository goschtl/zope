##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
This module handles the :startup directives. 

$Id: SiteDefinition.py,v 1.7 2002/12/11 18:07:25 gvanrossum Exp $
"""

import sys

# Import Configuration-related classes
from Zope.Configuration.Action import Action
from Zope.Configuration.INonEmptyDirective import INonEmptyDirective
from Zope.Configuration.ISubdirectiveHandler import ISubdirectiveHandler

# Import classes related to initial-services
from Zope.App.Traversing import traverse, traverseName
from ServerTypeRegistry import getServerType
from Zope.App.OFS.Services.ObjectHub.ObjectHub import ObjectHub
from Zope.App.OFS.Services.LocalEventService.LocalEventService import \
     LocalEventService
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration import \
     ServiceConfiguration

# Import Undo-related classes 
from Zope.ComponentArchitecture import getService
from Zope.App.Undo.ZODBUndoManager import ZODBUndoManager
from Zope.App.Undo.IUndoManager import IUndoManager
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.Server import ZLogIntegration
from Zope.Server.TaskThreads import ThreadedTaskDispatcher
from Zope.App.ZopePublication.ZopePublication import ZopePublication

from Persistence.Module import PersistentModuleImporter

import asyncore, zLOG

DEFAULT_STORAGE_FILE = 'Data.fs'
DEFAULT_LOG_FILE = 'STDERR'
DEFAULT_LOG_CLASS = 'Zope.Server.HTTPServer.CommonHitLogger'


class SiteDefinition:

    __class_implements__ = INonEmptyDirective    
    __implements__ = ISubdirectiveHandler

    # Some special file names for log files
    _special_log_files = {'STDERR': sys.stderr,
                          'STDOUT': sys.stdout}

    
    def __init__(self, _context, name="default", threads=4):
        """Initialize is called when defineSite directive is invoked."""
        self._name = name
        self._threads = int(threads)

        self._zodb = None
        self.useLog(_context)
        self._servers = {}

        self._started = 0


    def useFileStorage(self, _context, file=DEFAULT_STORAGE_FILE):
        """Lets you specify the ZODB to use."""
        from ZODB.FileStorage import DB
        self._zodb = DB(file)
        return []


    def useMappingStorage(self, _context):
        """Lets you specify the ZODB to use."""
        from ZODB.MappingStorage import DB
        self._zodb = DB()
        return []


    def useLog(self, _context, file=DEFAULT_LOG_FILE):
        """Lets you specify the log file to use"""

        if file in self._special_log_files.keys():
            file = self._special_log_files[file]
        else:
            file = open(file, 'a')

        zLOG._set_log_dest(file)
        return []


    def addServer(self, _context, type, port=None, verbose=None):
        """Add a new server for this site."""

        if port is not None:
            port = int(port)

        if verbose is not None:
            if verbose.lower() == 'true': verbose = 1
            else: verbose = 0

        if type is not None:
            self._servers[type] = {'port': port,
                                   'verbose': verbose}
        else:
            sys.stderr.out('Warning: Server of Type %s does not exist. ' +
                           'Directive neglected.') 
        return []


    def start(self):
        """Now start all the servers"""

        sys.stderr.write('\nStarting Site: %s\n\n' %self._name)

        sys.setcheckinterval(120)

        # setup undo fnctionality
        getService(None,"Utilities").provideUtility(
            IUndoManager,
            ZODBUndoManager(self._zodb)
            )

        # Setup the task dispatcher
        td = ThreadedTaskDispatcher()
        td.setThreadCount(self._threads)
        
        # check whether a root was already specified for this ZODB; if
        # not create one.
        self._initDB()

        # Start the servers
        for type, server_info in self._servers.items():

            server = getServerType(type)
            server.create(td, self._zodb, server_info['port'],
                          server_info['verbose'])

    def _initDB(self):
        """Initialize the ZODB and persistence module importer."""

        connection = self._zodb.open()
        root = connection.root()
        app = root.get(ZopePublication.root_name, None)

        if app is None:

            from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
            from Transaction import get_transaction
        
            app = RootFolder()
            self._addEssentialServices(app)
            root[ZopePublication.root_name] = app

            get_transaction().commit()

        connection.close()

        imp = PersistentModuleImporter()
        imp.install()


    def _addEssentialServices(self, root_folder):
        """Add essential services.

        XXX This ought to be configurable.  For now, hardcode an Event
        service and an ObjectHub.  I'll refactor later.

        XXX To reiterate, THIS IS AN EXAMPLE ONLY!!!  This code should
        be generalized.  Preferably, using marker interfaces,
        adapters, and a factory or two.  Oh, and don't forget
        metameta.zcml. :-)
        """

        sm = ServiceManager()
        root_folder.setServiceManager(sm)
        self._addService(root_folder, 'Events', LocalEventService)
        self._addService(root_folder, 'ObjectHub', ObjectHub)


    def _addService(self, root_folder, service_type, service_factory,
                    initial_status='Active'):
        """Add and configure a service to the root folder.

        The service is added to the default package and activated.
        This assumes the root folder already has a service manager,
        and that we add at most one service of each type.
        """
        # The code here is complicated by the fact that the registry
        # calls at the end require a fully context-wrapped
        # configuration; hence all the traverse[Name]() calls.
        # XXX Could we use the factory registry instead of the 3rd arg?
        package_name = ('', '++etc++Services', 'Packages', 'default')
        package = traverse(root_folder, package_name)
        name = service_type + '-1'
        service = service_factory()
        package.setObject(name, service)
        configuration_manager = traverseName(package, 'configure')
        configuration =  ServiceConfiguration(service_type,
                                              package_name + (name,))
        key = configuration_manager.setObject(None, configuration)
        configuration = traverseName(configuration_manager, key)
        configuration.status = initial_status


    def __call__(self):
        "Handle empty/simple declaration."
        return [ Action(discriminator = 'Start Servers',
                        callable = self.start,
                        args = ()),
                 ]
