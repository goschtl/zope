from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import implements

from zope.interface import Interface, implements
from zope.schema import TextLine, Set, Choice, Int, List

from ocql.interfaces import IDB
from ocql.database.metadata import MClass,Metadata,MetaType

# schema
class IAddress(Interface):
    street = TextLine(
        title=u"Street address",
        required=True
        )

class IDepartment(Interface):
    name = TextLine(
        title=u"name",
        required=True
        )
    address = Choice(
        title=u"Street address",
        vocabulary="vocab_of_IAddress",
        required=True
        )

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
    prerequisites = Set(
        title=u"Prerequisite courses",
        value_type = Choice(
            title=u"Course",
            vocabulary="vocab_of_ICourse",
            )
        )
    credits = Int(
        title=u"Credits",
        )
    assessment = List(
        title=u"Assessment",
        value_type = Int(
            title=u"Assessment",
            )
        )

class IPerson(Interface):
    name = TextLine(
        title=u"Name",
        required=True
        )

class IStaff(IPerson):
    department = Choice(
        title=u"Department",
        vocabulary="vocab_of_IDepartment",
        )
    teaches = Set(
        title=u"Teaches",
        value_type = Choice(
            title=u"Course",
            vocabulary="vocab_of_ICourse",
            )
        )
    salary = Int(
        title=u"Name",
        )

class IStudent(IPerson):
    major = Choice(
        title=u"Department",
        vocabulary="vocab_of_IDepartment",
        )
    supervisedBy = List(
        title=u"Supervised by",
        value_type = Choice(
            title=u"Member of staff",
            vocabulary="vocab_of_IStaff",
            )
        )
    takes = Set(
        title=u"Takes",
        value_type = Choice(
            title=u"Course",
            vocabulary="vocab_of_ICourse",
            )
        )

class ITutor(IStaff, IStudent):
    pass

class IVisitingStaff(IStaff):
    pass

class Address(object):
    implements(IAddress)

    def __init__(self, street):
        self.street =street

    def __repr__(self):
        return "%s <%s>" % (
            self.__class__.__name__,
            self.street
        )

class Department(object):
    implements(IDepartment)

    def __init__(self, name, address):
        self.name = name
        self.address = address

    def __repr__(self):
        return "%s <%s>" % (
            self.__class__.__name__,
            self.name
        )

class Course(object):
    implements(ICourse)

    def __init__(self, code, runBy, prerequisites, credits, assessment):
        self.code = code
        self.runBy = runBy
        self.prerequisites = prerequisites
        self.credits = credits
        self.assessment = assessment

    def __repr__(self):
        return "%s <%s>" % (
            self.__class__.__name__,
            self.code
        )

class Person(object):
    implements(IPerson)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "%s <%s>" % (
            self.__class__.__name__,
            self.name
        )

class Staff(Person):
    implements(IStaff)

    def __init__(self, name, department, teaches, salary):
        self.name= name
        self.department = department
        self.teaches = teaches
        self.salary = salary


class Student(Person):
    implements(IStudent)

    def __init__(self, name, major, supervisedBy, takes):
        self.name= name
        self.major = major
        self.supervisedBy = supervisedBy
        self.takes = takes

class Tutor(Staff, Student):
    implements(ITutor)

class VisitingStaff(Staff):
    implements(IVisitingStaff)

A1 = Address("Gibson Street")
A2 = Address("Hillhead Street")

D1 = Department("Computing Science", A1)
D2 = Department("Other department", A2)
D3 = Department("Department without curse", A2)

C1 = Course("C1", runBy = set([D1, D2]), prerequisites=set(), credits=2, assessment=set([0]))
C2 = Course("C2", runBy = set(), prerequisites=set([C1]), credits=3, assessment=set([1,2]))
C3 = Course("C3", runBy = set([D1]), prerequisites=set([C1, C2]), credits=3, assessment=set([1]))

S1 = Staff("S1", department=D1, teaches=set([C1]), salary=2000)
S2 = Staff("S2", department=D2, teaches=set([C1, C2]), salary=2500)

St1 = Student("St1", major=D1, supervisedBy=set([S1]), takes=set([C1, C2]))
St2 = Student("St2", major=D2, supervisedBy=set([S1, S2]), takes=set([C1]))

T1 = Tutor("T1", department=D1, teaches=set([C1]), salary=500)

V1 = VisitingStaff("V1", department=D1, teaches=set([C1]), salary=1000)

# metadata
class TestMetadata(Metadata):
    implements(IDB)
    adapts(None)

    db = {
            'IAddress': [A1, A2],
            'IDepartment': [D1, D2],
            'ICourse': [C1, C2, C3],
            'IStaff': [S1, S2],
            'IStudent': [St1, St2],
            'ITutor': [T1],
            'IVisitingStaff': [V1]
        }
    classes = {
            'IAddress': MClass(IAddress),
            'IDepartment': MClass(IDepartment),
            'ICourse': MClass(ICourse),
            'IStaff': MClass(IStaff),
            'IStudent': MClass(IStudent),
            'ITutor': MClass(ITutor),
            'IVisitingStaff': MClass(IVisitingStaff),
            }

    def __init__(self, context=None):
        pass

    def getAll(self, klass):
        x=self.db[klass]
        return x

    def get_class(self, name):
        return self.classes[name]