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

$Id: testZPTPage.py,v 1.7 2002/12/07 16:53:11 zagy Exp $
"""

import unittest

from Zope.App.OFS.Content.ZPTPage.ZPTPage import ZPTPage, \
     SearchableText, IZPTPage
from Zope.App.index.text.interfaces import ISearchableText
from Zope.ComponentArchitecture import getAdapter

# Wow, this is a lot of work. :(
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.App.Traversing.Traverser import Traverser
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
from Zope.App.Traversing.ITraversable import ITraversable
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter
from Zope.ContextWrapper import Wrapper
from Zope.Security.Checker import NamesChecker, defineChecker

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
