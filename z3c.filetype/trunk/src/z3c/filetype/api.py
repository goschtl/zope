##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""

$Id$
"""
from StringIO import StringIO
from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.contenttype import guess_content_type
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from z3c.filetype import magic, interfaces
from z3c.filetype.interfaces import filetypes
from z3c.filetype.event import FileTypeModifiedEvent


magicFile = magic.MagicFile()


def byMimeType(mt):
    """returns interfaces implemented by mimeType"""
    ifaces = [iface for name, iface in vars(filetypes).items()
              if name.startswith("I")]
    res = InterfaceSet()
    for iface in ifaces:
        mtm = iface.queryTaggedValue(filetypes.MTM)
        if mtm is not None:
            if mtm.match(mt):
               res.add(iface)
    return res


def getInterfacesFor(file=None, filename=None, mimeType=None):
    """returns a sequence of interfaces that are provided by file like
    objects (file argument) or string with an optional 
    filename as name or mimeType as mime-type 
    """
    ifaces = set()
    if file is not None:
        for mt in magicFile.detect(file):
            ifaces.update(byMimeType(mt))

    if mimeType is not None:
        ifaces.update(byMimeType(mimeType))

    if filename is not None and not ifaces:
        t = guess_content_type(filename)[0]
        # dont trust this here because zope does not recognize some
        # binary files.
        if t and not t == 'text/x-unknown-content-type':
            ifaces.update(byMimeType(t))

    if not ifaces:
        ifaces.add(filetypes.IBinaryFile)
    return InterfaceSet(*ifaces)


def applyInterfaces(obj):
    assert(interfaces.ITypeableFile.providedBy(obj))

    ifaces = InterfaceSet(*getInterfacesFor(obj.data))
    provided = set(interface.directlyProvidedBy(obj))
    for iface in provided:
        if not issubclass(iface, filetypes.ITypedFile):
            ifaces.add(iface)

    ifaces = set(ifaces)
    if ifaces and (ifaces != provided):
        clean_obj = removeAllProxies(obj)

        for iface in interface.directlyProvidedBy(clean_obj):
            if not iface.isOrExtends(filetypes.ITypedFile):
                ifaces.add(iface)

        interface.directlyProvides(clean_obj, ifaces)
        event.notify(FileTypeModifiedEvent(obj))
        return True
    return False


class InterfaceSet(object):
    """a set that only holds most specific interfaces

    >>> s = InterfaceSet(filetypes.IBinaryFile, filetypes.IImageFile)
    >>> sorted(s)
    [<InterfaceClass z3c.filetype.interfaces.filetypes.IBinaryFile>,
     <InterfaceClass z3c.filetype.interfaces.filetypes.IImageFile>]

    Now we add a jpeg file which is a subclass of all ifaces in the set
    >>> s.add(filetypes.IJPGFile)
    >>> sorted(s)
    [<InterfaceClass z3c.filetype.interfaces.filetypes.IJPGFile>]

    If we add a new which is not a subclass it is contained
    >>> s.add(filetypes.ITextFile)
    >>> sorted(s)
    [<InterfaceClass z3c.filetype.interfaces.filetypes.IJPGFile>,
     <InterfaceClass z3c.filetype.interfaces.filetypes.ITextFile>]
    """

    def __init__(self, *ifaces):
        self._data = set()
        for iface in ifaces:
            self.add(iface)

    def add(self, iface):
        assert(issubclass(iface, interface.Interface))
        toDelete = set()
        for i in self._data:
            if issubclass(i,iface):
                return
            if issubclass(iface, i):
                toDelete.add(i)
        self._data.add(iface)
        self._data.difference_update(toDelete)

    def __iter__(self):
        return iter(self._data)


@component.adapter(interfaces.ITypeableFile, IObjectModifiedEvent)
def handleModified(typeableFile, event):
    """handles modification of data"""
    if interfaces.IFileTypeModifiedEvent.providedBy(event):
        # do nothing if this is already a filetype modification event
        return
    applyInterfaces(typeableFile)


@component.adapter(interfaces.ITypeableFile, IObjectCreatedEvent)
def handleCreated(typeableFile, event):
    """handles modification of data"""
    applyInterfaces(typeableFile)
