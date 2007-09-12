##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""ZConfig data types

$Id$
"""

from ZODB.config import BaseConfig
from Zope2.Startup.datatypes import ZopeDatabase
from apelib.zope2.mapper import load_conf
from apelib.zodb3 import storage, db, resource


class Storage(BaseConfig):

    def open(self):
        config = self.config
        conns = {}
        for c in config.connections:
            conns[c.name] = c.open()
        conf = load_conf(config.mapper_variation, search_products=1)
        r = resource.StaticResource(conf)
        return storage.ApeStorage(
            conf_resource=r, connections=conns, name=self.name,
            debug_conflicts=config.debug_conflicts)


class Database(ZopeDatabase):

    def createDB(self, database_name, databases):
        config = self.config
        if config.mapper_variation:
            conf = load_conf(config.mapper_variation, search_products=1)
            r = resource.StaticResource(conf)
        else:
            r = None
        s = config.storage.open()
        kw = {}
        for name in ('scan_interval', 'pool_size', 'cache_size',
                     'version_pool_size', 'version_cache_size'):
            if hasattr(config, name):
                kw[name] = getattr(config, name)
        d = db.ApeDB(storage=s, conf_resource=r, **kw)
        return d


def getParams(config):
    kw = {}
    for name in config.__dict__.keys():
        if not name.startswith('_'):
            kw[name] = getattr(config, name)
    return kw


class FSConnection(BaseConfig):

    def open(self):
        from apelib.fs.connection import FSConnection as impl
        return impl(**getParams(self.config))


class DBAPIConnection(BaseConfig):

    def open(self):
        c = self.config
        return c.connection_class(
            module_name=c.module_name,
            connect_expression=c.connect_expression,
            prefix=c.prefix,
            )
