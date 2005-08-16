##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Basic tests for Page Templates used in content-space.

$Id$
"""

import unittest

from zope.interface.verify import verifyClass
from zope.security.interfaces import Forbidden

from zope.app.tests import ztapi
from zope.component import getView
from zope.publisher.browser import TestRequest
from zope.app.publisher.browser import BrowserView

# Wow, this is a lot of work. :(
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.adapters import Traverser, DefaultTraversable
from zope.app.traversing.interfaces import ITraverser, ITraversable
from zope.app.tests import ztapi
from zope.security.checker import NamesChecker, defineChecker
from zope.app.container.contained import contained

from zope.app.zptpage.interfaces import IZPTPage
from zope.app.zptpage.zptpage import ZPTPage, ZPTSourceView,\
     ZPTReadFile, ZPTWriteFile, ZPTFactory
from zope.app.zptpage.zptpage import Sized


class Data(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


class ZPTPageTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(ZPTPageTests, self).setUp()
        ztapi.provideAdapter(None, ITraverser, Traverser)
        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)
        defineChecker(Data, NamesChecker(['URL', 'name']))
        defineChecker(TestRequest, NamesChecker(['getPresentationSkin']))

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

        page = contained(page, Data(name='zope'))

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

        page = contained(page, Data(name='zope'))

        self.assertRaises(Forbidden, page.render, Data())

    def test_template_context_wrapping(self):

        class AU(BrowserView):
            def __str__(self):
                name = self.context.__name__
                if name is None:
                    return 'None'
                return name

        defineChecker(AU, NamesChecker(['__str__']))

        from zope.app.traversing.namespace import view
        ztapi.provideNamespaceHandler('view', view)
        ztapi.browserView(IZPTPage, 'name', AU)

        page = ZPTPage()
        page.setSource(
            u'<p tal:replace="template/@@name" />'
            )
        page = contained(page, None, name='zpt')
        request = TestRequest()
        self.assertEquals(page.render(request), 'zpt\n')


class DummyZPT(object):

    def __init__(self, source):
        self.source = source

    def getSource(self):
        return self.source

class SizedTests(unittest.TestCase):

    def testInterface(self):
        from zope.app.size.interfaces import ISized
        self.failUnless(ISized.implementedBy(Sized))
        self.failUnless(verifyClass(ISized, Sized))

    def test_zeroSized(self):
        s = Sized(DummyZPT(''))
        self.assertEqual(s.sizeForSorting(), ('line', 0))
        self.assertEqual(s.sizeForDisplay(), u'${lines} lines')
        self.assertEqual(s.sizeForDisplay().mapping, {'lines': '0'})

    def test_oneSized(self):
        s = Sized(DummyZPT('one line'))
        self.assertEqual(s.sizeForSorting(), ('line', 1))
        self.assertEqual(s.sizeForDisplay(), u'1 line')

    def test_arbitrarySize(self):
        s = Sized(DummyZPT('some line\n'*5))
        self.assertEqual(s.sizeForSorting(), ('line', 5))
        self.assertEqual(s.sizeForDisplay(), u'${lines} lines')
        self.assertEqual(s.sizeForDisplay().mapping, {'lines': '5'})


class TestFileEmulation(unittest.TestCase):

    def test_ReadFile(self):
        page = ZPTPage()
        content = u"<p></p>"
        page.setSource(content)        
        f = ZPTReadFile(page)
        self.assertEqual(f.read(), content)
        self.assertEqual(f.size(), len(content))

    def test_WriteFile(self):
        page = ZPTPage()
        f = ZPTWriteFile(page)
        content = "<p></p>"
        f.write(content)
        self.assertEqual(page.getSource(), content)

    def test_factory(self):
        content = "<p></p>"
        page = ZPTFactory(None)('foo', '', content)
        self.assertEqual(page.getSource(), content)


class ZPTSourceTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(ZPTSourceTest, self).setUp()
        ztapi.browserView(IZPTPage, 'source.html', ZPTSourceView)

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
