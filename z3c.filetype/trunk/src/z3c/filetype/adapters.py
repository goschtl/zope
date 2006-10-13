from zope.cachedescriptors.property import Lazy
import interfaces
from interfaces import filetypes
from zope import interface
from zope import component

class TypedFileType(object):

    interface.implements(interfaces.IFileType)
    component.adapts(filetypes.ITypedFile)

    def __init__(self, context):
        self.context = context

    @property
    def contentType(self):
        decl = interface.Declaration(
            *interface.directlyProvidedBy(self.context))
        for iface in decl.flattened():
            if not issubclass(iface, filetypes.ITypedFile):
                continue
            mt = iface.queryTaggedValue(filetypes.MT)
            if mt is not None:
                return mt

