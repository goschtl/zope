
from zope.interface import implements
from zope.component import adapts
from zope.component.interface import searchInterfaceUtilities
from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.app.catalog.interfaces import ICatalog
from zope.app.catalog.field import FieldIndex
from zope.app.intid import IIntIds
#import zc.relation.interfaces
from BTrees.IFBTree import difference

from ocql.interfaces import IDB
from ocql.database.index import AllIndex
from ocql.exceptions import ReanalyzeRequired

class MetaType:
    """Class to provide type details used by the database

    Might be used later, in case we want to do syntax and symbol
    checks before execution, e.g. in the parser.
    """

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
    """Class to provide details of an interface used by the database

    Might be used later, in case we want to do syntax and symbol
    checks before execution, e.g. in the parser.
    """

    def __init__(self, klass):
        self.klass = klass

    def is_collection(self):
        #not used
        return True

    def get_collection_type(self):
        """Returns always 'set' because this is the
        collection of instances of an interface
        """
        return set

    def get_contained(self):
        #not used
        return self.klass

    def __getitem__(self, fieldname):
        """Extract property information from the interface
        """
        x = self.klass[fieldname]._type
        try:
            return x[-1]
        except TypeError:
            return x


class Metadata:
    """Class to provide details and data of all the interfaces used
    by the database
    """

    implements(IDB)
    adapts(None)

    classes = None

    def __init__(self,context=None):
        #interfaces can be retrieved from the registry
        #as they are unusual to change
        self.classes = {}
        items = list(searchInterfaceUtilities(None))
        for name, iface in items:
            self.classes[iface.__name__] = MClass(iface)

        #catalogs = getUtilitiesFor(zc.relation.interfaces.ICatalog)
        #for name, catalog in catalogs:
        #    for index in catalog:
        #        results = catalog.iterValueIndexInfo()
        #        for result in results:
        #            continue
        #            #need to continue if this is required

    def getAll(self, klassname):
        """Return all instances of the given interface as a list

            >>> from ocql.testing import utils
            >>> utils.setupInterfaces(None)
            >>> utils.setupCatalog(None)

            >>> db = IDB(None)
            >>> result = db.getAll('IStudent')
            >>> type(result)
            <type 'list'>
            >>> sorted(result, key=lambda x:x.name)
            [Student <Ann>, Student <Charith>, Student <Jane>, Student <Stewart>]
        """
        #objects have to be retrieved always on call
        #as they are subject to change

        catalogs = getUtilitiesFor(ICatalog)
        intids = getUtility(IIntIds)
        for name, catalog in catalogs:
            for iname, index in catalog.items():
                if isinstance(index, AllIndex):
                    if index.interface.__name__ == klassname:
                        results = catalog.apply({iname:(1,1)})
                        obj_list = [intids.getObject(result) for result in results]
                        return obj_list

    def getFromIndex(self, klass, property, operator, value):
        """Return all instances of the given interface as a list

            >>> from ocql.testing import utils_opt
            >>> utils_opt.setupInterfaces(None)
            >>> utils_opt.setupCatalog(None)

            >>> db = IDB(None)
            >>> result = db.getFromIndex('IOptimizedClass', 'value', '<=', 5)
            >>> type(result)
            <type 'list'>
            >>> sorted(result, key=lambda x:x.name)
            [Opt: 0, Opt: 1, Opt: 2, Opt: 3, Opt: 4, Opt: 5]
        """
        catalogs = getUtilitiesFor(ICatalog)
        intids = getUtility(IIntIds)
        for name, catalog in catalogs:
            for iname, index in catalog.items():
                if isinstance(index, FieldIndex) and \
                index.field_name == property and \
                index.interface.__name__ == klass:
                    if operator == '==':
                        results = catalog.apply({iname:(value, value)})
                    elif operator == '!=':
                        all = catalog.apply({iname:(None, None)})
                        temp = catalog.apply({iname:(value, value)})
                        results = difference(all, temp)
                    elif operator == '>=':
                        results = catalog.apply({iname:(value, None)})
                    elif operator == '>':
                        lt_eq = catalog.apply({iname:(value, None)})
                        temp = catalog.apply({iname:(value, value)})
                        results = difference(lt_eq, temp)
                    elif operator == '<=':
                        results = catalog.apply({iname:(None, value)})
                    elif operator == '<':
                        gt_eq = catalog.apply({iname:(None, value)})
                        temp = catalog.apply({iname:(value, value)})
                        results = difference(gt_eq, temp)

                    obj_list = [intids.getObject(result) for result in results]
                    return obj_list

        raise ReanalyzeRequired()

    def hasPropertyIndex(self, klass, property):
        """Check if an interface's property has a FieldIndex

            >>> from ocql.testing import utils_opt
            >>> utils_opt.setupInterfaces(None)
            >>> utils_opt.setupCatalog(None)

            >>> db = IDB(None)
            >>> db.hasPropertyIndex('IHalfOptimizedClass', 'name')
            True
            >>> db.hasPropertyIndex('IHalfOptimizedClass', 'valueNoOpt')
            False
        """
        catalogs = getUtilitiesFor(ICatalog)
        for name, catalog in catalogs:
            for iname, index in catalog.items():
                if isinstance(index, FieldIndex) and \
                index.field_name == property and \
                index.interface.__name__ == klass:
                    return True
        return False

    def get_class(self, klassname):
        """Returns a MetaType instance for the class."""
        return self.classes[klassname]
