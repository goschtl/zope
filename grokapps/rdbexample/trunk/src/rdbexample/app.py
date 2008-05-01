import grok
from megrok import rdb

class rdbexample(grok.Application, grok.Model):
    def __init__(self):
        pass

    def traverse(self, name):
        if name == 'departments':
            self.departments = Departments()
            

class Index(grok.View):
    pass # see app_templates/index.pt


class Departments(rdb.Container):
    pass

class Department(rdb.Model):
    pass
