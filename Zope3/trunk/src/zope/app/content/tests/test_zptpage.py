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

$Id: test_zptpage.py,v 1.2 2002/12/25 14:12:48 jim Exp $
"""

import unittest

from zope.app.content.zpt import ZPTPage, \
     SearchableText, IZPTPage
from zope.app.interfaces.index.text.interfaces import ISearchableText
from zope.component import getAdapter

# Wow, this is a lot of work. :(
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.traverser import Traverser
from zope.app.interfaces.traversing.traverser import ITraverser
from zope.app.traversing.defaulttraversable import DefaultTraversable
from zope.app.interfaces.traversing.traversable import ITraversable
from zope.component.adapter import provideAdapter
from zope.proxy.context import Wrapper
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
            '<span tal:replace="context/name">splat</span>'
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



def test_suite():
    return unittest.makeSuite(ZPTPageTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
