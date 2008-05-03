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
            return rdb.query(Faculty).get(int(name))
        except ValueError:
            return None

class FacultyList(grok.View):
    grok.name('index')
    grok.context(RDBExample)

    def render(self):
        result = ""
        for faculty in rdb.query(Faculty).all():
            result += "%i - %s\n" % (faculty.id, faculty.title)
        return result


class Departments(rdb.Container):
    pass


class DepartmentTraverse(grok.Traverser):
    grok.context(Departments)
    def traverse(self, name):
        try:
            return self.context[int(name)]
        except ValueError:
            return None

class Faculty(rdb.Model):
    # rdb.table_name('faculty') is the default
    __tablename__ = 'faculty'

    # XXX note that rdb.Model s don't support traversal using traverse methods;
    # it does work using external grok.Traversers
    def traverse(self, name):
        pass

    grok.traversable('departments')

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String(50))

    departments = relation('Department',
                           backref='faculty',
                           collection_class=Departments)

class FacultyTraverse(grok.Traverser):
    grok.context(Faculty)

    def traverse(self, name):
        if name == 'departments':
            return self.context.departments

class Department(rdb.Model):
    __tablename__ = 'department'

    id = Column('id', Integer, primary_key=True)
    faculty_id = Column('faculty_id', Integer, ForeignKey('faculty.id'))
    title = Column('title', String(50))


class DepartmentView(grok.View):
    grok.name('index')
    grok.context(Department)

    def render(self):
        return "Department: %i - %s" % (self.context.id, self.context.title)

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
        return rdb.Fields(Faculty())

    @grok.action('add')
    def handle_add(self, *args, **kw):
        print kw
