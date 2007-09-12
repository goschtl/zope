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
"""Bits useful for configuration.  May move to its own package.

$Id$
"""

import xml.sax.handler
from xml.sax import parse

from apelib.zodb3 import zodbtables


class Directive:
    """Abstract base class for table-oriented directives.
    """

    schema = None  # override

    def __init__(self, source, *args, **kw):
        self.source = source
        if args:
            columns = self.schema.get_columns()
            for n in range(len(args)):
                key = columns[n].name
                if kw.has_key(key):
                    raise TypeError(
                        '%s supplied as both positional and keyword argument'
                        % repr(key))
                kw[key] = args[n]
        self.data = kw
        unique_key = [self.__class__]
        for column in self.schema.columns:
            if column.primary:
                unique_key.append(kw[column.name])
        self.unique_key = tuple(unique_key)

    def get_unique_key(self):
        return self.unique_key

    def index(self, tables):
        t = tables.get(self.__class__)
        if t is None:
            t = zodbtables.Table(self.schema)
            tables[self.__class__] = t
        t.insert(self.data)

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return other.data == self.data
        return 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<%s from %s with %s>" % (
            self.__class__.__name__, repr(self.source), repr(self.data))



class XMLConfigReader (xml.sax.handler.ContentHandler):
    """Reads configuration from XML files.
    """

    def __init__(self, handlers):
        self.handlers = handlers
        # Set up a directive list in a default variation.
        directives = []
        self.variations = {'': directives}
        self.stack = [{'directives': directives,
                       'variations': self.variations}]
        self.locator = None

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, name, attrs):
        vars = self.stack[-1].copy()
        self.stack.append(vars)
        handler = self.handlers[name]
        locator = self.locator
        if locator is not None:
            source = (locator.getSystemId(), locator.getLineNumber())
        else:
            source = ("unknown", 0)
        handler(source, vars, attrs)

    def endElement(self, name):
        del self.stack[-1]
        


class DirectiveReader:

    def __init__(self, handlers):
        self.directives = {}  # { unique key -> variation -> directive }
        self.handlers = handlers

    def read(self, filename):
        reader = XMLConfigReader(self.handlers)
        parse(filename, reader)
        for vname, directives in reader.variations.items():
            self.add(directives, vname)

    def add(self, directives, vname):
        for d in directives:
            key = d.get_unique_key()
            info = self.directives.setdefault(key, {})
            if info.has_key(vname):
                if d == info[vname]:
                    # OK
                    pass
                else:
                    raise KeyError(
                        'Conflicting directives: %s != %s' % (
                        repr(d), repr(info[vname])))
            else:
                info[vname] = d

    def get_directives(self, vname=''):
        res = []
        # Note that although there isn't a way to declare that a
        # variation extends another variation, all variations should
        # derive from the default anyway, so we don't need the
        # extension mechanism yet.
        if not vname:
            vnames = ('',)
        else:
            vnames = (vname, '')
        for key, info in self.directives.items():
            for vn in vnames:
                if info.has_key(vn):
                    res.append(info[vn])
                    break  # Go to next directive
        return res



class DirectiveTables:

    def __init__(self, directives):
        self.tables = {}      # {table name -> table}
        for d in directives:
            d.index(self.tables)

    def query(self, table_name, **filter):
        """Returns the specified directive records.
        """
        t = self.tables.get(table_name)
        if t is None:
            return []
        return t.select(filter)

    def query_field(self, table_name, field, **filter):
        t = self.tables.get(table_name)
        if t is None:
            return None
        records = t.select(filter)
        if len(records) > 1:
            raise LookupError, "More than one record returned from field query"
        if not records:
            return None
        return records[0][field]



class ComponentSystem:

    def __init__(self, directives):
        self.dtables = DirectiveTables(directives)
        self.factories = {}   # {comptype -> assembler factory}
        self.components = {}  # {(comptype, name) -> component}

    def add_component_type(self, comptype, assembler_factory):
        self.factories[comptype] = assembler_factory

    def get(self, comptype, name):
        obj = self.components.get((comptype, name))
        if obj is not None:
            return obj
        f = self.factories[comptype]
        assembler = f(self, comptype, name)
        obj = assembler.create()
        self.components[(comptype, name)] = obj
        assembler.configure()
        return obj


