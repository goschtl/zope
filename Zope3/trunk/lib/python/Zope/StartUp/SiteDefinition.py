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

$Id: SiteDefinition.py,v 1.3 2002/07/18 22:26:46 jeremy Exp $
"""

import sys

# Import Configuration-related classes
from Zope.Configuration.Action import Action
from Zope.Configuration.ConfigurationDirectiveInterfaces \
     import INonEmptyDirective

from ServerTypeRegistry import getServerType

# Import Undo-related classes 
from Zope.ComponentArchitecture import getService
from Zope.App.Undo.ZODBUndoManager import ZODBUndoManager
from Zope.App.Undo.IUndoManager import IUndoManager


from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
import asyncore, zLOG
from Zope.Server import ZLogIntegration
from Zope.Server.TaskThreads import ThreadedTaskDispatcher
from Zope.App.ZopePublication.ZopePublication import ZopePublication

import asyncore, zLOG

DEFAULT_STORAGE_FILE = 'Data.fs'
DEFAULT_LOG_FILE = 'STDERR'
DEFAULT_LOG_CLASS = 'Zope.Server.HTTPServer.CommonHitLogger'


class SiteDefinition:

    __class_implements__ = INonEmptyDirective    

    # Some special file names for log files
    _special_log_files = {'STDERR': sys.stderr,
                          'STDOUT': sys.stdout}

    
    def __init__(self, _context, name="default", threads=4):
        """Initilize is called, when the defineSite directive is invoked.
        """
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
        self._zodb = DB(file)
        return []


    def useLog(self, _context, file=DEFAULT_LOG_FILE):
        """Lets you specify the log file to use"""

        if file in self._special_log_files.keys():
            file = self._special_log_files[file]
        else:
            file = open(file, 'w')

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
        """Initialize the ZODB"""

        connection = self._zodb.open()
        root = connection.root()
        app = root.get(ZopePublication.root_name, None)

        if app is None:

            from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
            from Transaction import get_transaction
        
            app = RootFolder()
            root[ZopePublication.root_name] = app

            get_transaction().commit()

        connection.close()


    def __call__(self):
        "Handle empty/simple declaration."
        return [ Action(discriminator = 'Start Servers',
                        callable = self.start,
                        args = ()),
                 ]
