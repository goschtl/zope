"""This module sets up views for models to publish them to the web.

We also define the non-persistent Departments object.

See db.py for the relational database configuration,
and url.py for the URL configuration.
"""

import grok
from megrok import traject
from z3c.saconfig import Session
from zope.interface import Interface
from zope import schema

from trajectrdbexample import db

class IFaculty(Interface):
    title = schema.TextLine(title=u"Title")

class IDepartment(Interface):
    title = schema.TextLine(title=u"Title")

class TrajectRDBExample(grok.Application, grok.Model):
    pass
        
class TrajectRDBExampleIndex(grok.View):
    """The index page. This shows all faculties available.
    """ 
    grok.name('index')
    grok.context(TrajectRDBExample)

    def faculties(self):
        session = Session()
        site = grok.getSite()
        for faculty in session.query(db.Faculty):
            # we must locate the faculty before we can do
            # security checks on it or get its URL.
            # locating means it'll get a __parent__ and __name__
            # attribute. See auto-locate adapter below though.
            traject.locate(site, faculty, None)
            yield faculty
    
class AddFaculty(grok.AddForm):
    grok.context(TrajectRDBExample)

    form_fields = grok.Fields(IFaculty)

    @grok.action('add')
    def handle_add(self, *args, **kw):
        faculty = db.Faculty(**kw)
        session = Session()
        session.add(faculty)
        self.redirect(self.url(self.context))

class FacultyIndex(grok.View):
    """This is the default view for Faculty.
    """
    grok.name('index')
    grok.context(db.Faculty)
        
class Departments(grok.Context):
    """This non-persistent object exists to attach views to it.

    It could also grow knowledge about how to query and add departments.
    """
    def __init__(self, faculty_id):
        self.faculty_id = faculty_id

    def departments(self):
        # we must locate again
        # the context is the site object
        site = grok.getSite()
        for department in self.__parent__.departments:
            traject.locate(site, department, None)
            yield department
    
class AddDepartment(grok.AddForm):
    grok.context(Departments)

    form_fields = grok.Fields(IDepartment)

    @grok.action('add')
    def handle_add(self, *args, **kw):
        department = db.Department(**kw)
        self.context.__parent__.departments.append(department)
        # also could do:
        # department.faculty_id = self.context.faculty_id

        self.redirect(self.url(self.context))

class DepartmentsIndex(grok.View):
    grok.name('index')
    grok.context(Departments)

class DepartmentIndex(grok.View):
    grok.name('index')
    grok.context(db.Department)

# Example of an adapter to auto-locate models.
# this is one for db.Faculty.

# If your models have a common base class or interface, you can
# register an absolute URL adapter for all in one go.
    
# Note that you'll still need to locate before doing security checks
# on objects.

# from zope.traversing.browser.interfaces import IAbsoluteURL
# from zope.traversing.browser import AbsoluteURL
# from zope.publisher.interfaces.http import IHTTPRequest

# class TrajectAbsoluteURL(AbsoluteURL, grok.MultiAdapter):
#     """Make sure that our objects can have absolute URLs.

#     This can be done by using traject to locate them and then just
#     generating the URL as normal.
#     """
#     grok.provides(IAbsoluteURL)
#     grok.adapts(db.Faculty, IHTTPRequest)
    
#     def __str__(self):
#         traject.locate(grok.getSite(), self.context, None)
#         return super(TrajectAbsoluteURL, self).__str__()
    
#     __call__ = __str__
