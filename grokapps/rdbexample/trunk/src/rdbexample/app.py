import grok
from megrok import rdb

from zope.interface.interfaces import IInterface



from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation


class Database(rdb.Database):

    url = 'postgres:///rdbexample'


class RDBExample(grok.Application, grok.Model):
    def traverse(self, name):
        try:
            key = int(name)
        except ValueError:
            return None
        return rdb.query(Faculty).get(key)

class FacultyList(grok.View):
    grok.name('index')
    grok.context(RDBExample)

    def render(self):
        result = ""
        for faculty in rdb.query(Faculty).all():
            result += "%s - %s (%s)" % (faculty.id, faculty.title,
                                        self.url(str(faculty.id)))
        return result


class Departments(rdb.Container):
    rdb.key('title')

class Faculty(rdb.Model):
    # rdb.table_name('faculty') is the default
    __tablename__ = 'faculty'

    grok.traversable('departments')

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(50))

    departments = relation('Department',
                           backref='faculty',
                           collection_class=Departments)

class Department(rdb.Model):
    __tablename__ = 'department'

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
        d = Department(**kw)
        self.context.set(d)


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
        f = Faculty(**kw)
        rdb.session().save(f)
        #import pdb; pdb.set_trace()
