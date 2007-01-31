from zope.app.container.contained import Contained, setitem, uncontained
import root
from zope import interface
import interfaces
from zope.schema.fieldproperty import FieldProperty
from zope.app.container.interfaces import IContained

class MountpointContainer(root.DBRoot, Contained):
    
    interface.implements(interfaces.IMountpointContainer)
    
    dbName = FieldProperty(interfaces.IMountpointContainer['dbName'])

    def get(self, key, default=None):
        '''See interface `IReadContainer`'''
        try:
            self.__getitem__(key)
        except KeyError:
            return default

    def items(self):
        '''See interface `IReadContainer`'''
        return [(k,self.__getitem__(k)) for k in self.keys()]

    def values(self):
        '''See interface `IReadContainer`'''
        return [self.__getitem__(k) for k in self.keys()]

    def __getitem__(self, key):
        #XXX why do we have to do this?
        # cross references should work
        item = self._data.__getitem__(key)
        if hasattr(item, '__parent__'):
            item.__parent__ = self
        return item

    def __setitem__(self, key, object):
        '''See interface `IWriteContainer`'''
        setitem(self, self._data.__setitem__, key, object)

    def __delitem__(self, key):
        '''See interface `IWriteContainer`'''
        uncontained(self._data[key], self, key)
        del self._data[key]

