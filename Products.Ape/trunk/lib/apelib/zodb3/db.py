##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Extension of the ZODB DB class

$Id$
"""

import cPickle
import cStringIO

from threading import RLock
from transaction import Transaction
from ZODB.DB import DB
from apelib.core.interfaces import ConfigurationError

from connection import ApeConnection
from storage import ApeStorage
from resource import StaticResource
from interfaces import IResourceAccess


def call_conf_factory(factory, kw):
    """Returns (conf, conns) given the name of a factory and arguments.
    """
    pos = factory.rfind('.')
    if pos < 0:
        raise ConfigurationError(
            'factory must be a string containing <module>.<name>')
    module = factory[:pos]
    name = factory[pos + 1:]
    m = __import__(module, {}, {}, (name,))
    f = getattr(m, name)
    return f(**kw)


class ApeDB (DB):
    """Mapper-driven Database
    """

    klass = ApeConnection
    database_name = "unnamed"

    # SDH: some extra args.
    def __init__(self, storage,
                 conf_resource=None,
                 factory=None,
                 scan_interval=10,
                 pool_size=7,
                 cache_size=400,
                 cache_deactivate_after=60,
                 version_pool_size=3,
                 version_cache_size=100,
                 version_cache_deactivate_after=10,
                 **kw
                 ):
        """Create an object database.
        """
        if conf_resource is None:
            if factory is not None:
                # Use a configuration factory
                conf, connections = call_conf_factory(factory, kw)
                conf_resource = StaticResource(conf)
            else:
                if kw:
                    raise ConfigurationError('Extra keyword args: %s' % kw)
                if isinstance(storage, ApeStorage):
                    # Use the configuration from the storage
                    conf_resource = storage.conf_resource
                else:
                    raise ConfigurationError(
                        'No configuration or factory specified')
        else:
            # conf_resource was specified
            if kw:
                raise ConfigurationError('Extra keyword args: %s' % kw)
            assert IResourceAccess.isImplementedBy(conf_resource)
            assert factory is None
        
        # Allocate locks:
        l = RLock()
        self._a=l.acquire
        self._r=l.release

        # Setup connection pools and cache info
        self._pools={}
        self._temps=[]
        self._pool_size=pool_size
        self._cache_size=cache_size
        self._cache_deactivate_after = cache_deactivate_after
        self._version_pool_size=version_pool_size
        self._version_cache_size=version_cache_size
        self._version_cache_deactivate_after = version_cache_deactivate_after

        self._miv_cache={}

        # Setup storage
        self._storage=storage
        storage.registerDB(self)
        if not hasattr(storage,'tpc_vote'): storage.tpc_vote=lambda *args: None

        self._conf_resource = conf_resource
        scan_interval = int(scan_interval)
        if scan_interval > 0:
            from scanner import PoolScanControl, Scanner
            pool_ctl = PoolScanControl(storage, db=self, scan_interval=scan_interval)
            self.pool_scan_ctl = pool_ctl
            scanner = Scanner()
            storage.scanner = scanner
            scanner.storage = storage
        else:
            self._scan_ctl = None

        # Pass through methods:
        self.history = storage.history

        if hasattr(storage, 'undoInfo'):
            self.undoInfo=storage.undoInfo

        # Create the root object if it doesn't exist
        c = self.open()
        try:
            c._prepare_root()
        finally:
            c.close()
