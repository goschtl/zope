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
"""Zope 2 mapper creation

$Id$
"""

import os
import Products
from apelib.config.apeconf import configure


def load_conf(vname, search_products=0):
    """Builds a mapper from apeconf.xml files.
    """
    here = os.path.dirname(__file__)
    filenames = [os.path.join(here, 'apeconf.xml')]
    if search_products:
        seen = {}  # Product name -> 1
        for path in Products.__path__:
            for name in os.listdir(path):
                if not seen.has_key(name):
                    seen[name] = 1
                    fn = os.path.join(path, name, 'apeconf.xml')
                    if os.path.exists(fn):
                        filenames.append(fn)
    return configure(filenames, vname)


def create_fs_mapper(basepath, **kw):
    """Filesystem mapper factory.

    Returns (mapper, { name -> connection })

    Usage in database configuration file:
    factory=apelib.zope2.mapper.create_fs_mapper
    basepath=/var/zope/data
    """
    from apelib.fs.connection import FSConnection

    mapper = load_conf('filesystem', search_products=1)
    conn = FSConnection(basepath, **kw)
    return mapper, {'fs': conn}


def create_sql_mapper(module_name, **kw):
    """SQL mapper factory.

    Returns (mapper, { name -> connection })

    Usage in database configuration file:
    factory=apelib.zope2.mapper.create_sql_mapper
    module_name=psycopg
    params=
    kwparams=
    table_prefix=zodb
    """
    from apelib.sql.dbapi import DBAPIConnector

    mapper = load_conf('sql', search_products=1)
    conn = DBAPIConnector(module_name, **kw)
    return mapper, {'db': conn}

