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

$Id: sitedefinition.py,v 1.15 2003/05/01 19:35:36 faassen Exp $
"""

from zope.interface import classProvides
import logging
import sys

# Importing zlogintegration redirects asyncore's logging to the
# logging module
from zope.server import zlogintegration

# Import Configuration-related classes
from zope.configuration.action import Action
from zope.configuration.interfaces import INonEmptyDirective
from zope.configuration.interfaces import ISubdirectiveHandler

from zope.app.startup import bootstrap
from zope.app.startup.servertyperegistry import getServerType

# Import Undo-related classes
from zope.app.interfaces.undo import IUndoManager
from zope.app.browser.undo import ZODBUndoManager
from zope.component import getService
from zope.app.services.servicenames import Utilities
from zope.server.taskthreads import ThreadedTaskDispatcher

from zodb.db import DB
from zodb.code.module import PersistentModuleImporter
from zope.app.services.interface import register

DEFAULT_STORAGE_FILE = 'Data.fs'
DEFAULT_LOG_FILE = 'STDERR'
DEFAULT_LOG_LEVEL = 'INFO'
# We show INFO level log messages by default because that's how the
# service startup messages showing the host and port used for various
# protocols are logged.


class SiteDefinition:

    classProvides(INonEmptyDirective)
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
        self._servers = []

        self._started = 0

    def close(self):
        if self._zodb is not None:
            self._zodb.close()
            self._zodb = None

    #
    # Storage directives
    #

    def useFileStorage(self, _context, file=DEFAULT_STORAGE_FILE):
        """Specify a FileStorage."""
        from zodb.storage.file import FileStorage
        if self._zodb is not None:
            raise RuntimeError("Database already open")
        self._zodb = DB(FileStorage(file))
        return []

    def useMappingStorage(self, _context):
        """Specify a MappingStorage - no undo or versions."""
        from zodb.storage.mapping import MappingStorage
        if self._zodb is not None:
            raise RuntimeError("Database already open")
        self._zodb = DB(MappingStorage())
        return []

    def useBDBFullStorage(self, _context, **kws):
        """Specify a Berkeley full storage."""
        from zodb.config import convertBDBStorageArgs
        from zodb.storage.bdbfull import BDBFullStorage
        kws = convertBDBStorageArgs(**kws)
        self._zodb = DB(BDBFullStorage(**kws))
        return []

    def useMemoryFullStorage(self, _context, **kws):
        """Specify a full memory storage."""
        from zodb.config import convertBDBStorageArgs
        from zodb.storage.memory import MemoryFullStorage
        kws = convertBDBStorageArgs(**kws)
        self._zodb = DB(MemoryFullStorage(**kws))
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
            self._servers.append((type, {'port': port, 'verbose': verbose}))
        else:
            sys.stderr.out('Warning: Server of Type %s does not exist. ' +
                           'Directive neglected.')
        return []


    def start(self):
        """Now start all the servers"""

        sys.stderr.write('\nStarting Site: %s\n\n' %self._name)

        sys.setcheckinterval(120)

        # setup undo fnctionality
        getService(None,Utilities).provideUtility(
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
        for type, server_info in self._servers:

            server = getServerType(type)
            server.create(td, self._zodb, server_info['port'],
                          server_info['verbose'])

    def _initDB(self):
        """Initialize the ZODB and persistence module importer."""

        bootstrap.bootstrapInstance(self._zodb)

        imp = PersistentModuleImporter()
        imp.install()
        register()

    def __call__(self):
        "Handle empty/simple declaration."
        return [ Action(discriminator = 'Start Servers',
                        callable = self.start,
                        args = ()),
                 ]
