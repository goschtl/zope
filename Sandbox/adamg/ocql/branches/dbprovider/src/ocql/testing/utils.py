# -*- coding: UTF-8 -*-

"""Utilities for testing support

$Id$
"""

from zope import interface, component
from zope.component.interface import provideInterface

from zope.app.catalog.catalog import Catalog
from zope.app.catalog.interfaces import ICatalog
from zope.app.catalog.field import FieldIndex
from ocql.database.index import AllIndex

from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds

from zope.app.keyreference.testing import SimpleKeyReference

from ocql.testing.sample.interfaces import IOrganization
from ocql.testing.sample.interfaces import IProject
from ocql.testing.sample.interfaces import IStudent
from ocql.testing.sample.interfaces import IMentor

from ocql.testing.sample.mentor import Mentor
from ocql.testing.sample.project import Project
from ocql.testing.sample.student import Student
from ocql.testing.sample.organization import Organization

def setupInterfaces(test):
    provideInterface('', IOrganization)
    provideInterface('', IProject)
    provideInterface('', IStudent)
    provideInterface('', IMentor)

def setupCatalog(test):
    intids = IntIds()
    component.provideUtility(intids, IIntIds)
    component.provideAdapter(SimpleKeyReference)

    cat = Catalog()

    cat['org_name'] = FieldIndex('name', IOrganization)

    cat['proj_name'] = FieldIndex('name', IProject)
    cat['proj_descr'] = FieldIndex('description', IProject)

    cat['student_name'] = FieldIndex('name', IStudent)

    cat['mentor_name'] = FieldIndex('name', IMentor)

    cat['all_students'] = AllIndex(IStudent)
    cat['all_mentors'] = AllIndex(IMentor)
    cat['all_projects'] = AllIndex(IProject)
    cat['all_orgs'] = AllIndex(IOrganization)

    m1 = Mentor()
    m1.name = u"John Doe"
    id = intids.register(m1)
    cat.index_doc(id, m1)

    p1 = Project()
    p1.name = u"Save the world"
    p1.description = u""
    id = intids.register(p1)
    cat.index_doc(id, p1)

    s1 = Student()
    s1.name = u"Charith"
    id = intids.register(s1)
    cat.index_doc(id, s1)

    s2 = Student()
    s2.name = u"Jane"
    id = intids.register(s2)
    cat.index_doc(id, s2)

    s3 = Student()
    s3.name = u"Ann"
    id = intids.register(s3)
    cat.index_doc(id, s3)

    o1 = Organization()
    o1.name = u"Zope.org"
    id = intids.register(o1)
    cat.index_doc(id, o1)

    component.provideUtility(cat, ICatalog, name='foo-catalog')

def queryCatalog():
    cat = component.getUtility(ICatalog, name='foo-catalog')
    intids = component.getUtility(IIntIds)

    results = cat.apply({'student_name':('Charith','Charith')})

    for r in results:
        obj = intids.getObject(r)
        print obj

    results = cat.apply({'all_students':(1,1)})

    for r in results:
        obj = intids.getObject(r)
        print obj