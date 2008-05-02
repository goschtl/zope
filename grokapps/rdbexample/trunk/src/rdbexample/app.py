import grok
from megrok import rdb

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import relation


class Database(rdb.Database):

    url = 'postgres:///rdbexample'


class RDBExample(grok.Application, grok.Model):

    def traverse(self, name):
        return rdb.query(Faculty).get(int(name))


class Index(grok.View):

    grok.context(RDBExample)


class Departments(rdb.Container):
    pass


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


class FacultyIndex(grok.View):
    grok.name('index.html')
    grok.context(Faculty)
    grok.template('faculty')


class DepartmentList(grok.View):
    grok.name('index.html')
    grok.context(Departments)
    grok.template('departments')
