import grok
from megrok import rdb

from zope.location.location import located

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation

from z3c.saconfig import EngineFactory, GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory, IEngineCreatedEvent

# we set up the engine factory and the session
# we set them up as global utilities here. It is also possible to
# use a local engine factory and a special locally scoped session
TEST_DSN = 'sqlite:///:memory:'

engine_factory = EngineFactory(TEST_DSN)
scoped_session = GloballyScopedSession()

grok.global_utility(engine_factory, direct=True)
grok.global_utility(scoped_session, direct=True)

# we set up the SQLAlchemy metadata object to which we'll associate all the
# SQLAlchemy-backed objects
metadata = rdb.MetaData()

# we declare to megrok.rdb that all SQLAlchemy-managed mapped instances
# are associated with this metadata. This directive can also be used
# on a per rdb.Model subclass basis
rdb.metadata(metadata)

# we make sure that when the engine is created we set up the metadata for it
@grok.subscribe(IEngineCreatedEvent)
def setUpDatabase(event):
    rdb.setupDatabase(metadata)

class RDBExample(grok.Application, grok.Model, rdb.QueryContainer):
    """The application object.

    We mix in grok.Model to make it persistent so it can be installed using
    the Grok UI.
    
    We mix in rdb.QueryContainer to let it behave like a container. We
    need to implement the query method to supply it with a query object.
    """
    def query(self):
        session = rdb.Session()
        # we allow browsing into any Faculty object
        # we could've restricted this query so that it would only
        # allow browsing to a subset
        return session.query(Faculty)

class RDBExampleIndex(grok.View):
    """The index page for RDBExample. This shows all faculties available.
    """
    grok.name('index')
    grok.context(RDBExample)

    def faculties(self):
        session = rdb.Session()
        for faculty in session.query(Faculty).all():
            yield located(faculty, self.context, str(faculty.id))

class AddFaculty(grok.AddForm):
    """A form to add a new Faculty object to the application.
    """
    grok.context(RDBExample)

    @property
    def form_fields(self):
        return rdb.Fields(Faculty)

    @grok.action('add')
    def handle_add(self, *args, **kw):
        faculty = Faculty(**kw)
        session = rdb.Session()
        session.add(faculty)
        self.redirect(self.url(self.context))

class Departments(rdb.Container):
    """This container implements the departments relation on Faculty.
    """

    # we browse to departments using the title attribute of Department,
    # which is assumed (or constrained) to be unique. By default this
    # would use the primary key of Department for browsing.
    rdb.key('title')
        
class Faculty(rdb.Model):
    """This model implements the faculty content object.

    It's backed by a relational database.
    """
    
    # we declare that the departments atribute can be browsed into
    grok.traversable('departments')

    # the attributes of a faculty, stored in the database
    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(50))

    # we declare a relation, using our special Departments class
    departments = relation('Department',
                           backref='faculty',
                           collection_class=Departments)

class FacultyIndex(grok.View):
    """This is the default view for Faculty.
    """
    grok.name('index')
    grok.context(Faculty)
        
class Department(rdb.Model):
    """This model implements the department content object.

    Each department is in a faculty.
    
    It's backed by a relational database.
    """

    # the attributes of a department
    id = Column('id', Integer, primary_key=True)
    # the id of the faculty that this department is in
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
        self.redirect(self.url(self.context))
            
class DepartmentIndex(grok.View):
    grok.name('index')
    grok.context(Department)

class DepartmentsIndex(grok.View):
    grok.name('index')
    grok.context(Departments)

