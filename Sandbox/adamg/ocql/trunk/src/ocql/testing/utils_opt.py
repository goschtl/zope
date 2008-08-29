# -*- coding: UTF-8 -*-

"""Utilities for testing support

$Id$
"""

from zope import interface, component
from zope.component.interface import provideInterface

from zope.schema import Text, TextLine, Int

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

#import zc.relation.catalog
#import zc.relation.interfaces
#import zc.relation.queryfactory
import BTrees


class IOptimizedClass(interface.Interface):
    name = TextLine(title=u"Name")
    value = Int(title=u"value")

class IUnOptimizedClass(interface.Interface):
    name = TextLine(title=u"Name")
    value = Int(title=u"value")

class IHalfOptimizedClass(interface.Interface):
    name = TextLine(title=u"Name")
    valueOpt = Int(title=u"value")
    valueNoOpt = Int(title=u"value")

class OptimizedClass(object):
    interface.implements(IOptimizedClass)

    name = u''
    value = 0

    def __repr__(self):
        return "Opt: %s" % self.name

class UnOptimizedClass(object):
    interface.implements(IUnOptimizedClass)

    name = u''
    value = 0

    def __repr__(self):
        return "UnOpt: %s" % self.name

class HalfOptimizedClass(object):
    interface.implements(IHalfOptimizedClass)

    name = u''
    valueOpt = 0
    valueNoOpt = 0

    def __repr__(self):
        return "HalfOpt: %s" % self.name

def setupInterfaces(test):
    provideInterface('', IOptimizedClass)
    provideInterface('', IUnOptimizedClass)
    provideInterface('', IHalfOptimizedClass)

def setupCatalog(test, optCount=10, unoptCount=10, halfCount=10):
    intids = IntIds()
    component.provideUtility(intids, IIntIds)
    component.provideAdapter(SimpleKeyReference)
    cat = Catalog()

    cat['opt_name'] = FieldIndex('name', IOptimizedClass)
    cat['opt_value'] = FieldIndex('value', IOptimizedClass)

    cat['half_name'] = FieldIndex('name', IHalfOptimizedClass)
    cat['half_valueOpt'] = FieldIndex('value', IHalfOptimizedClass)

    cat['all_opt'] = AllIndex(IOptimizedClass)
    cat['all_unopt'] = AllIndex(IUnOptimizedClass)
    cat['all_half'] = AllIndex(IHalfOptimizedClass)

    for i in range(optCount):
        o = OptimizedClass()
        o.value = i
        o.name = unicode(i)
        id = intids.register(o)
        cat.index_doc(id, o)

    for i in range(unoptCount):
        o = UnOptimizedClass()
        o.value = i
        o.name = unicode(i)
        id = intids.register(o)
        cat.index_doc(id, o)

    for i in range(halfCount):
        o = HalfOptimizedClass()
        o.valueOpt = i
        o.valueNoOpt = i
        o.name = unicode(i)
        id = intids.register(o)
        cat.index_doc(id, o)

    component.provideUtility(cat, ICatalog, name='boo-catalog')
