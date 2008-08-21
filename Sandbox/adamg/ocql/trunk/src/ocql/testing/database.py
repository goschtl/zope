from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import implements

from zope.interface import Interface, implements
from zope.schema import TextLine, Set, Choice, Int, List

from ocql.interfaces import IDB
from ocql.database.metadata import MClass,Metadata,MetaType

# schema
class ICourse(Interface):
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

class Department(object):
    implements(IDepartments)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "%s <%s>" % (
            self.__class__.__name__,
            self.name
        )

class Course(object):
    implements(ICourse)

    def __init__(self, code, runBy, credits):
        self.code = code
        self.runBy = runBy
        self.credits = credits

    def __repr__(self):
        return "%s <%s>" % (
            self.__class__.__name__,
            self.code
        )

D1 = Department("Computing Science")
D2 = Department("Other department")
D3 = Department("Department without curse")

C1 = Course("C1", runBy = set([D1, D2]), credits=2)
C2 = Course("C2", runBy = set(), credits=3)
C3 = Course("C3", runBy = set([D1]), credits=3)


# metadata
class TestMetadata(Metadata):
    implements(IDB)
    adapts(None)

    db = {
            'IDepartments': [D1, D2],
            'ICourse': [C1, C2, C3]
        }
    classes = {
            'IDepartments': MClass(IDepartments),
            'ICourse': MClass(ICourse),
            }

    def __init__(self, context=None):
        pass

    def getAll(self, klass):
        x=self.db[klass]
        return x

    def get_class(self, name):
        return self.classes[name]