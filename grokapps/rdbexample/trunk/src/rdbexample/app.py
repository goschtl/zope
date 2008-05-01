import grok
from megrok import rdb
from sqlalchemy.orm import *  # XXX


class RDBExample(grok.Application, grok.Model):
    def __init__(self):
        pass

    def traverse(self, name):
        return rdb.query(Faculty).get(name)

    
class Index(grok.View):
    pass


class Faculty(rdb.Model):
    # rdb.table_name('faculty') is the default

    id = Column('id', Integer, primary_key=True)
    title = Column('email', String(50))

    departments = relation('Department',
                           backref='faculty',
                           collection_class=Departments)

    def traverse(self, name):
        return self.departments.get(name)
    
    
class Departments(rdb.Container):
    pass

class Department(rdb.Model):
    faculty_id = Column('faculty_id', Integer, ForeignKey(Faculty.id))
    
class DepartmentList(grok.View):
    grok.context(Faculty)
    def render(self):
        result = ""
        for department in self.context.departments.values():
            result += department.title + '\n'
        return result
