##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Basic tests for Page Templates used in content-space.

$Id: test_zptpage.py,v 1.12 2003/06/01 15:59:30 jim Exp $
"""

import unittest

from zope.interface.verify import verifyClass
from zope.exceptions import Forbidden

import zope.app.content.zpt
from zope.app.content.zpt import ZPTPage, SearchableText, ZPTSourceView
from zope.app.interfaces.content.zpt import IZPTPage
from zope.app.interfaces.index.text import ISearchableText
from zope.component import getAdapter, getView
from zope.component.view import provideView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.browser import TestRequest, BrowserView

# Wow, this is a lot of work. :(
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.adapters import Traverser, DefaultTraversable
from zope.app.interfaces.traversing import ITraverser
from zope.app.interfaces.traversing import ITraversable
from zope.component.adapter import provideAdapter
from zope.app.context import ContextWrapper
from zope.context import Wrapper, getInnerWrapperData
from zope.security.checker import NamesChecker, defineChecker

class Data(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


class ZPTPageTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(None, ITraverser, Traverser)
        provideAdapter(None, ITraversable, DefaultTraversable)
        provideAdapter(IZPTPage, ISearchableText, SearchableText)
        defineChecker(Data, NamesChecker(['URL', 'name']))
        defineChecker(TestRequest, NamesChecker(['getPresentationType',
                                                 'getPresentationSkin']))

    def testSearchableText(self):
        page = ZPTPage()
        searchableText = getAdapter(page, ISearchableText)

        utext = u'another test\n' # The source will grow a newline if ommited
        html = u"<html><body>%s</body></html>\n" % (utext, )

        page.setSource(utext)
        self.failUnlessEqual(searchableText.getSearchableText(), [utext])

        page.setSource(html, content_type='text/html')
        self.assertEqual(searchableText.getSearchableText(), [utext+'\n'])

        page.setSource(html, content_type='text/plain')
        self.assertEqual(searchableText.getSearchableText(), [html])

    def testZPTRendering(self):
        page = ZPTPage()
        page.setSource(
            u''
            '<html>'
            '<head><title tal:content="options/title">blah</title></head>'
            '<body>'
            '<a href="foo" tal:attributes="href request/URL/1">'
            '<span tal:replace="container/name">splat</span>'
            '</a></body></html>'
            )

        page = Wrapper(page, Data(name='zope'))

        out = page.render(Data(URL={'1': 'http://foo.com/'}),
                          title="Zope rules")
        out = ' '.join(out.split())

        self.assertEqual(
            out,
            '<html><head><title>Zope rules</title></head><body>'
            '<a href="http://foo.com/">'
            'zope'
            '</a></body></html>'
            )

    def test_request_protected(self):
        page = ZPTPage()
        page.setSource(
            u'<p tal:content="python: request.__dict__" />'
            )

        page = Wrapper(page, Data(name='zope'))

        self.assertRaises(Forbidden, page.render, Data())

    def test_template_context_wrapping(self):

        class AU(BrowserView):
            def __str__(self):
                dict = getInnerWrapperData(self.context)
                return str(dict and dict.get('name') or None)

        from zope.app.traversing.namespace import provideNamespaceHandler
        from zope.app.traversing.namespace import view
        provideNamespaceHandler('view', view)
        provideView(IZPTPage, 'name', IBrowserPresentation, AU)

        page = ZPTPage()
        page.setSource(
            u'<p tal:replace="template/@@name" />'
            )
        page = ContextWrapper(page, None, name='zpt')
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        self.assertEquals(page.render(request), 'zpt\n')


class DummyZPT:

    def __init__(self, source):
        self.source = source

    def getSource(self):
        return self.source

class SizedTests(unittest.TestCase):

    def testInterface(self):
        from zope.app.interfaces.size import ISized
        from zope.app.content.zpt import Sized
        self.failUnless(ISized.isImplementedByInstancesOf(Sized))
        self.failUnless(verifyClass(ISized, Sized))

    def test_zeroSized(self):
        from zope.app.content.zpt import Sized
        s = Sized(DummyZPT(''))
        self.assertEqual(s.sizeForSorting(), ('line', 0))
        self.assertEqual(s.sizeForDisplay(), u'0 lines')

    def test_oneSized(self):
        from zope.app.content.zpt import Sized
        s = Sized(DummyZPT('one line'))
        self.assertEqual(s.sizeForSorting(), ('line', 1))
        self.assertEqual(s.sizeForDisplay(), u'1 line')

    def test_arbitrarySize(self):
        from zope.app.content.zpt import Sized
        s = Sized(DummyZPT('some line\n'*5))
        self.assertEqual(s.sizeForSorting(), ('line', 5))
        self.assertEqual(s.sizeForDisplay(), u'5 lines')


class TestFileEmulation(unittest.TestCase):

    def test_ReadFile(self):
        page = zope.app.content.zpt.ZPTPage()
        content = u"<p></p>"
        page.setSource(content)        
        f = zope.app.content.zpt.ZPTReadFile(page)
        self.assertEqual(f.read(), content)
        self.assertEqual(f.size(), len(content))

    def test_WriteFile(self):
        page = zope.app.content.zpt.ZPTPage()
        f = zope.app.content.zpt.ZPTWriteFile(page)
        content = "<p></p>"
        f.write(content)
        self.assertEqual(page.getSource(), content)

    def test_factory(self):
        content = "<p></p>"
        page = zope.app.content.zpt.ZPTFactory(None)('foo', '', content)
        self.assertEqual(page.getSource(), content)


class ZPTSourceTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideView(IZPTPage, 'source.html', IBrowserPresentation, ZPTSourceView)

    def testSourceView(self):
        page = ZPTPage()

        utext = u'another test\n' # The source will grow a newline if ommited
        html = u"<html><body>%s</body></html>\n" % (utext, )
        page.setSource(html, content_type='text/plain')
        request = TestRequest()

        view = getView(page, 'source.html', request)

        self.assertEqual(str(view), html)
        self.assertEqual(view(), html)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZPTPageTests),
        unittest.makeSuite(SizedTests),
        unittest.makeSuite(TestFileEmulation),
        unittest.makeSuite(ZPTSourceTest),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
