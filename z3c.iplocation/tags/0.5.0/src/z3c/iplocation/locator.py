##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""IP Locator Implementation.

$Id$
"""
__docformat__ = "reStructuredText"

import csv
import StringIO
import persistent
import zope.app.intid
import zope.interface
import zope.location
from BTrees import IOBTree, IFBTree, OIBTree
from zc.catalog import index
from zope.app.container import contained
from zope.schema.fieldproperty import FieldProperty

from z3c.iplocation import interfaces


def getIP(decimal):
    pieces = []
    for pos in xrange(4):
        piece = decimal/(256**(3-pos))
        pieces.append(str(piece))
        decimal -= piece*256**(3-pos)
    return '.'.join(pieces)


def getDecimal(ip):
    return sum(
        [int(piece)*(256**(3-pos))
         for pos, piece in enumerate(ip.split('.'))])


class Location(persistent.Persistent):
    zope.interface.implements(interfaces.ILocation)

    ipFrom = FieldProperty(interfaces.ILocation['ipFrom'])
    ipTo = FieldProperty(interfaces.ILocation['ipTo'])
    name = FieldProperty(interfaces.ILocation['name'])

    def __init__(self, ipFrom, ipTo, name):
        self.ipFrom = ipFrom
        self.ipTo = ipTo
        self.name = name

    def __repr__(self):
        return '<%s %s-%s %r>' %(
            self.__class__.__name__, self.ipFrom, self.ipTo, self.name)


class IPLocator(contained.Contained, persistent.Persistent):
    """A persistent IP Locator implementation."""
    zope.interface.implements(
        interfaces.IIPLocator, interfaces.IIPLocatorManagement)

    def __init__(self):
        super(IPLocator, self).__init__()
        self.reset()

    def reset(self):
        self._locations = OIBTree.OITreeSet()
        self._ids = zope.app.intid.IntIds()
        self._ipFrom = index.ValueIndex()
        self._ipTo = index.ValueIndex()

    def update(self, file, klass=None, skipLines=5):
        self.reset()
        counter = 0
        if klass is None:
            raise ValueError("Must use a ipligence location class.")
        try:
            # probably we've got file upload data from a form
            if isinstance(file, str):
                reader = csv.reader(StringIO.StringIO(file))
            else:
                reader = csv.reader(file)
            for row in reader:
                counter += 1
                if skipLines < counter:
                    loc = klass(*row)
                    self.add(loc, loc.decimalFrom, loc.decimalTo)
        except TypeError:
            raise ValueError("Wrong ipligence location class used or skipped "
                             "the wrong amount of skipLines.")

    def get(self, ip, default=None):
        """See interfaces.IIPLocator"""
        ip = getDecimal(ip)
        fromResult = self._ipFrom.apply(
            {'between': (None, ip, False, False)})
        toResult = self._ipTo.apply(
            {'between': (ip, None, False, False)})
        result = IFBTree.intersection(fromResult, toResult)
        if not result:
            return default
        return self._ids.getObject(result[0])

    def add(self, location, fromDecimal=None, toDecimal=None):
        """See interfaces.IIPLocatorManagement

        The ``fromDecimal`` and ``toDecimal`` optional arguments are designed
        to save the conversion, if the IPs already exist in decimal format.
        """
        if location in self._locations.keys():
            return
        self._locations.insert(location)
        # give em a location and prevent to run into NotYet errors in IIntIds
        zope.location.locate(location, self)
        uid = self._ids.register(location)
        self._ipFrom.index_doc(uid, fromDecimal or getDecimal(location.ipFrom))
        self._ipTo.index_doc(uid, toDecimal or getDecimal(location.ipTo))

    def remove(self, location):
        """See interfaces.IIPLocatorManagement"""
        if location not in self._locations:
            return
        uid = self._ids.getId(location)
        self._ipFrom.unindex_doc(uid)
        self._ipTo.unindex_doc(uid)
        self._ids.unregister(location)
        self._locations.remove(location)
