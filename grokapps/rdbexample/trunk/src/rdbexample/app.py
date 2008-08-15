import grok
from megrok import rdb

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation

from z3c.saconfig import EngineFactory, GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory, IEngineCreatedEvent

TEST_DSN = 'sqlite:///:memory:'
  
engine_factory = EngineFactory(TEST_DSN)
scoped_session = GloballyScopedSession()

grok.global_utility(engine_factory, direct=True)
grok.global_utility(scoped_session, direct=True)

metadata = rdb.MetaData()

class RDBExample(grok.Application, grok.Model):
    def traverse(self, name):
        try:
            key = int(name)
        except ValueError:
            return None
        session = rdb.Session()
        return session.query(Faculty).get(key)

@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    rdb.setupDatabase(metadata)

class FacultyList(grok.View):
    grok.name('index')
    grok.context(RDBExample)

    def render(self):
        result = ""
        session = rdb.Session()
        for faculty in session.query(Faculty).all():
            result += "%s - %s (%s)" % (faculty.id, faculty.title,
                                        self.url(str(faculty.id)))
        return result

class Departments(rdb.Container):
    rdb.key('title')

class Faculty(rdb.Model):
    grok.traversable('departments')

    rdb.metadata(metadata)
    
    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(50))

    departments = relation('Department',
                           backref='faculty',
                           collection_class=Departments)

class Department(rdb.Model):
    rdb.metadata(metadata)
    
    id = Column('id', Integer, primary_key=True)
    faculty_id = Column('faculty_id', Integer, ForeignKey('faculty.id'))
    title = Column('title', String(50))

class AddDepartment(grok.AddForm):
    grok.context(Departments)

    @property
    def form_fields(self):
        return rdb.Fields(Department)

    @grok.action('add')
    def handle_add(self, *args, **kw):
        department = Department(**kw)
        session = rdb.Session()
        session.add(department)
        self.context.set(department)

class DepartmentView(grok.View):
    grok.name('index')
    grok.context(Department)

    def render(self):
        return "Department: %r - %r" % (self.context.id, self.context.title)

class DepartmentList(grok.View):
    grok.name('index')
    grok.context(Faculty)

    def render(self):
        result = "Faculty: %s - %s " % (self.context.id, self.context.title)
        for department in self.context.departments.values():
            result += department.title + '\n'
        return result

class DepartmentsView(grok.View):
    grok.name('index')
    grok.context(Departments)

    def render(self):
        result = ""
        for department in self.context.values():
            result += department.title + '\n'
        return result

class AddFaculty(grok.AddForm):
    grok.context(RDBExample)

    @property
    def form_fields(self):
        return rdb.Fields(Faculty)

    @grok.action('add')
    def handle_add(self, *args, **kw):
        faculty = Faculty(**kw)
        session = rdb.Session()
        session.add(faculty)
