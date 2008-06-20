
from zope.interface import implements
from zope.component import adapts
from zope.component.interface import searchInterfaceUtilities 
from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid import IIntIds

from ocql.interfaces import IDB
from ocql.database.index import IAllIndex
 
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

class Metadata:
    implements(IDB)
    adapts(None)
    
    db={}
    classes = {}
    
    def __init__(self):
        items = list(searchInterfaceUtilities(self))
        catalogs = getUtilitiesFor(ICatalog)
        intids = getUtility(IIntIds)
        #import pydevd;pydevd.settrace()
        for i in catalogs:
            catalog = getUtility(ICatalog,name=i[0].__str__())
            for index in catalog:
                #is this the correct way to filter?
                if index.split("_")[0] == 'all':
                    results = catalog.apply({index:(1,1)})
                    obj_list = []
                    for result in results:
                        obj = intids.getObject(result)
                        obj_list.append(obj)
                    self.db.__setitem__(index,obj_list)
        
        #seems the db is correct
        print self.db
        
        #still this need to be corrected. I was unable to get index.interface property
        for item in items:
            class_name = item[0].rsplit('.',1)[1].__str__()
            self.classes.__setitem__(class_name,class_name)
        print self.classes
           

    def get_class(self, classname):
        """Returns a MetaType instance for the class."""