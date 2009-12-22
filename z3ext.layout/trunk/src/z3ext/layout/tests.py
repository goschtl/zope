##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED 'AS IS' AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
import unittest, doctest, sys
from zope import interface, component
from zope.app.testing import setup
from zope.container.sample import SampleContainer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import NotFound
from zope.error.error import ErrorReportingUtility
from zope.error.interfaces import IErrorReportingUtility
from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.pt import expressions
from z3c.pt.pagetemplate import \
    ViewPageTemplateFile as ViewPageTemplateFilePT

from z3ext.layout import pagelet
from z3ext.layout.expressions import PageletTranslator


class IFolder1(interface.Interface):
    pass

class IFolder1_1(interface.Interface):
    pass

class IFolder1_1_1(interface.Interface):
    pass

class ITestPagelet(interface.Interface):
    pass


class Folder(SampleContainer):
    pass


class MyLayout(object):

    title = u'My layout'


class simple(BrowserView):
    interface.implements(IBrowserPublisher)

    def __call__(self, *args, **kw):
        return self.index(*args, **kw)


def SimpleViewClass(src, offering=None, bases=(), name=u'', pt=True):
    if offering is None:
        offering = sys._getframe(1).f_globals

    bases += (simple, )

    if pt:
        class_ = type("SimpleViewClass PT from %s" % src, bases,
                      {'index': ViewPageTemplateFilePT(src, offering),
                       '__name__': name})
    else:
        class_ = type("SimpleViewClass from %s" % src, bases,
                      {'index': ViewPageTemplateFile(src, offering),
                       '__name__': name})

    return class_


def setUp(test):
    root = setup.placefulSetUp(site=True)
    root.__name__ = 'root'
    test.globs['root'] = root
    component.provideAdapter(pagelet.queryDefaultView)
    component.provideAdapter(pagelet.PageletPublisher, name='pagelet')
    component.provideAdapter(pagelet.PageletObjectPublisher,name='pageletObject')
    component.provideUtility(expressions.path_translator, name='path')
    component.provideUtility(PageletTranslator(), name="pagelet")
    component.provideUtility(ErrorReportingUtility(), IErrorReportingUtility)

    setup.setUpTestAsModule(test, 'z3ext.layout.TESTS')


def tearDown(test):
    setup.placefulTearDown()
    setup.tearDownTestAsModule(test)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'pagelet.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'zcml.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))
