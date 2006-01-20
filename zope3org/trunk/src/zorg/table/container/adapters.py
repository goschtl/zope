from interfaces import IMovableLocation
from zope.interface import implements
from zope.app.copypastemove.interfaces import IContainerItemRenamer

class MovableLocation(object):

    implements(IMovableLocation)

    def __init__(self,context):
        self.context = context
        self.__parent__ = self.context.__parent__

    def _setName(self,v):
        old = self.context.__name__
        if v != old:
            renamer = IContainerItemRenamer(self.__parent__)
            renamer.renameItem(old, v)
        
    def _getName(self):
        print "MovalbeLocation._getName"
        return self.context.__name__

    __name__ = property(_getName,_setName)
    
