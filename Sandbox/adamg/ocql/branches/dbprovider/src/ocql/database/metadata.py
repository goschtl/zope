
from zope.interface import implements
from zope.component import adapts
from zope.component.interface import searchInterfaceUtilities 
from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid import IIntIds

from ocql.interfaces import IDB
from ocql.database.index import AllIndex
#from ocql.testing.database import MClass

class MetaType:
    def get_property(self, name):
        """
            Get type information and metadata for property.
            Returns a MetaType
        """

    def is_collection(self):
        """Returns True if the represented type is a collection."""

    def get_collection_type(self):
        """Returns the represented type"""

    def get_contained(self):
        """
            Throws an exception if represented type is not a collection, or
            the contained type if a collection
        """

    def get_size(self):
        """Returns the size of the collection or class if known"""


class MClass(MetaType):
    #interface suspect thing
    def __init__(self, klass):
        self.klass = klass

    def is_collection(self):
        return True

    def get_collection_type(self):
        return set

    def get_contained(self):
        return self.klass

    def __getitem__(self, name):
        x = self.klass[name]._type
        try:
            return x[-1]
        except TypeError:
            return x


class Metadata:
    implements(IDB)
    adapts(None)
    
    db= {}

    classes = {}
    
    def __init__(self,context=None):
        #all the interfaces are retrieved from the catalog
        #items = list(searchInterfaceUtilities(self))
        catalogs = getUtilitiesFor(ICatalog)
        intids = getUtility(IIntIds)
        for i in catalogs:
            catalog = i[1]
            for index in catalog:
                if isinstance(catalog[index], AllIndex):
                    interface =  catalog[index].interface
                    results = catalog.apply({index:(1,1)})
                    obj_list = []
                    for result in results:
                        obj = intids.getObject(result)
                        obj_list.append(obj)
                    self.db.__setitem__(interface.__name__,obj_list)
                    self.classes.__setitem__(interface.__name__,MClass(interface))
        
        #seems db and classes are correctly filled
        #print self.db
        #print self.classes
        

    def getAll(self, klass):
        return self.db[klass]
    
    def get_class(self, classname):
        """Returns a MetaType instance for the class."""
        return self.classes[classname]
    