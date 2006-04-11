from interfaces import IMovableLocation
from zope.interface import implements
from zope.app.copypastemove.interfaces import IContainerItemRenamer
from multiform.interfaces import IFormLocation
from zope.security.proxy import removeSecurityProxy

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
            if IFormLocation.providedBy(self.context):
                # if we are in a multiform, we have to add the request
                # data to our prefix
                form = removeSecurityProxy(self.context.__form__)
                oldPrefix = form.prefix
                newPrefix = form.prefix[:-len(old)] + v
                for oldKey in list(form.request.form.keys()):
                    if oldKey.startswith(oldPrefix):
                        newKey = newPrefix + oldKey[len(oldPrefix):]
                        form.request.form[newKey]=form.request.form[oldKey]
                
    def _getName(self):
        return self.context.__name__

    __name__ = property(_getName,_setName)
    
