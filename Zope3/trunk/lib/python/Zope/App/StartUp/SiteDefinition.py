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

$Id: SiteDefinition.py,v 1.13 2002/12/20 19:46:01 jeremy Exp $
"""

import sys
import logging
import asyncore

# Import Configuration-related classes
from Zope.Configuration.Action import Action
from Zope.Configuration.INonEmptyDirective import INonEmptyDirective
from Zope.Configuration.ISubdirectiveHandler import ISubdirectiveHandler

from ServerTypeRegistry import getServerType

# Import Undo-related classes 
from Zope.ComponentArchitecture import getService
from Zope.App.Undo.ZODBUndoManager import ZODBUndoManager
from Zope.App.Undo.IUndoManager import IUndoManager
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.Server.TaskThreads import ThreadedTaskDispatcher
from Zope.App.ZopePublication.ZopePublication import ZopePublication

from Persistence.Module import PersistentModuleImporter

DEFAULT_STORAGE_FILE = 'Data.fs'
DEFAULT_LOG_FILE = 'STDERR'
DEFAULT_LOG_LEVEL = 'INFO'


class SiteDefinition:

    __class_implements__ = INonEmptyDirective    
    __implements__ = ISubdirectiveHandler

    # Some special file names for log files
    _special_log_files = {'STDERR': sys.stderr,
                          'STDOUT': sys.stdout}

    # Mapping from log level names to numeric log levels
    _log_levels = {
        'CRITICAL' : logging.CRITICAL,
        'ERROR' : logging.ERROR,
        'WARN' : logging.WARN,
        'INFO' : logging.INFO,
        'DEBUG' : logging.DEBUG,
        'NOTSET' : logging.NOTSET,
        }

    
    def __init__(self, _context, name="default", threads=4):
        """Initialize is called when defineSite directive is invoked."""
        self._name = name
        self._threads = int(threads)

        self._zodb = None
        self.useLog(_context)
        self._servers = {}

        self._started = 0

    def close(self):
        if self._zodb is not None:
            self._zodb.close()
            self._zodb = None

    def useFileStorage(self, _context, file=DEFAULT_STORAGE_FILE):
        """Lets you specify the ZODB to use."""
        from ZODB.FileStorage import DB
        if self._zodb is not None:
            raise RuntimeError("Database already open")
        self._zodb = DB(file)
        return []


    def useMappingStorage(self, _context):
        """Lets you specify the ZODB to use."""
        from ZODB.MappingStorage import DB
        if self._zodb is not None:
            raise RuntimeError("Database already open")
        self._zodb = DB()
        return []


    def useLog(self, _context, file=DEFAULT_LOG_FILE, level=DEFAULT_LOG_LEVEL):
        """Lets you specify the log file and level to use"""

        # Translate the level to logging
        loglevel = self._log_levels.get(level.upper())
        if loglevel is None:
            raise ValueError, "unknown log level %r" % level

        # Get the root logger and set its logging level
        root = logging.root
        root.setLevel(loglevel)

        # Remove previous handlers
        for h in root.handlers[:]:
            root.removeHandler(h)

        # Create the new handler
        if file in self._special_log_files.keys():
            file = self._special_log_files[file]
            handler = logging.StreamHandler(file)
        else:
            handler = logging.FileHandler(file)

        # Create a standard Zope-style formatter and set it
        formatter = logging.Formatter(
            "------\n"
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S")
        handler.setFormatter(formatter)

        # Set the handler
        root.addHandler(handler)

        # Return empty sequence to satisfy API
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

        from Zope.App.StartUp import bootstrap
        bootstrap.bootstrapInstance(self._zodb)

        imp = PersistentModuleImporter()
        imp.install()


    def __call__(self):
        "Handle empty/simple declaration."
        return [ Action(discriminator = 'Start Servers',
                        callable = self.start,
                        args = ()),
                 ]
