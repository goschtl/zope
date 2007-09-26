from zope.interface import Interface, implements
from zope.schema import TextLine, Set, Choice, Int, List
from ocql.engine import metadata

# schema
class ICurses(Interface):
    code = TextLine(
        title=u"Course code",
        required=True
        )
    runBy = List(
        title=u"Run by",
        value_type = Choice(
            title=u"Department",
            vocabulary="vocab_of_IDepartment",
            )
        )
    credits = Int(
        title=u"Credits",
        )

class IDepartments(Interface):
    name = TextLine(
        title=u"name",
        required=True
        )
    address = Choice(
        title=u"Street address",
        vocabulary="vocab_of_IAddress",
        required=True
        )

class MClass(metadata.MetaType):
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
    
class MType(metadata.MetaType):
    def __init__(self, klass, collection_type=None):
        self.klass = klass
        self.collection_type = collection_type

    def is_collection(self):
        return (self.collection_type is not None)

    def get_collection_type(self):
        return self.collection_type
    
    def get_contained(self):
        return self.klass

class Department(object):
    implements(IDepartments)
    
    def __init__(self, name):
        self.name = name

class Curses(object):
    implements(ICurses)
    
    def __init__(self, code, runBy, credits):
        self.code = code
        self.runBy = runBy
        self.credits = credits

D1 = Department("Computing Science")
D2 = Department("Other department")
D3 = Department("Department without curse")

C1 = Curses("C1", runBy = set([D1, D2]), credits=2)
C2 = Curses("C2", runBy = set(), credits=3)
C3 = Curses("C3", runBy = set([D1]), credits=3)


# metadata
class TestMetadata(metadata.Metadata):
    db = {
            'IDepartments': [D1, D2],
            'ICurses': [C1, C2, C3]
        }
    classes = {
            'IDepartments': MClass(IDepartments),
            'ICurses': MClass(ICurses),
            }
    
    def getAll(self, klass):
        x=self.db[klass]
        return x
    
    def get_class(self, name):
        return self.classes[name]
    
    def get_collection_type(self, name):
        klass = self.get_class(name)
        rv = klass.get_collection_type()
        return rv