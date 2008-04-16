from zope import interface
from zope.app.component import site, hooks
from zope.app.folder import folder
from zope.app.container import contained
from zope.app.security import interfaces as security_ifaces

from z3c.metrics import index, interfaces

class IFooDocIndex(interfaces.IIndex): pass
class IBarDocIndex(interfaces.IIndex): pass
class ICreatorIndex(interfaces.IIndex): pass

class IDocument(interface.Interface): pass
class IDescendant(interface.Interface): pass

def setUpRoot():
    root = folder.rootFolder()
    sm = site.LocalSiteManager(root)
    root.setSiteManager(sm)
    hooks.setSite(root)
    return root

class Principal(contained.Contained):
    interface.implements(security_ifaces.IPrincipal)

    @property
    def id(self):
        return self.__name__

class Authentication(folder.Folder):
    interface.implements(security_ifaces.IAuthentication)

    getPrincipal = folder.Folder.__getitem__

class Index(index.Index):

    def _getKeyFor(self, obj):
        return id(obj)

class FooDocIndex(Index):
    interface.implements(IFooDocIndex)

class BarDocIndex(Index):
    interface.implements(IBarDocIndex)

class CreatorIndex(Index):
    interface.implements(ICreatorIndex)

class Created(folder.Folder):
    interface.implements(interfaces.ICreated)

    creators = ()

class Document(Created):
    interface.implements(IDocument)

class Descendant(Created):
    interface.implements(IDescendant)

    @apply
    def created():
        """Callable created field attribute"""
        def get(self):
            return lambda: self.__dict__['created']
        def set(self, value):
            self.__dict__['created'] = value
        return property(get, set)
