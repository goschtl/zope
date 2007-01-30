from zope.app.container.contained import Contained, setitem, uncontained
import root
from zope import interface
import interfaces
from zope.schema.fieldproperty import FieldProperty

class MountpointContainer(root.DBRoot, Contained):
    
    interface.implements(interfaces.IMountpointContainer)
    
    dbName = FieldProperty(interfaces.IMountpointContainer['dbName'])

    def __setitem__(self, key, object):
        '''See interface `IWriteContainer`'''
        setitem(self, self._data.__setitem__, key, object)

    def __delitem__(self, key):
        '''See interface `IWriteContainer`'''
        uncontained(self._data[key], self, key)
        del self._data[key]

