##########################################################################
# zopyx.smartprintng.core 
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


"""
Tests, tests, tests.........
"""

import unittest

from zope.interface.verify import verifyClass
import zopyx.smartprintng.core.transformation as transformation
from zopyx.smartprintng.core.interfaces import IHTMLTransformation

html = """
<a href="http://www.heise.de" />HEISE</A>
<a href="@@control-panel" > Control Panel</a>
<a HREF="#anchor">
<a href="http://www.heise.de#anchor" />HEISE</A>
<A   HrEF="/foo/bar" />foo bar</A>
<a href="http://foo.com"><em>bar</em></a>
"""


class TransformationTests(unittest.TestCase):

    def testInterfaces(self):
        verifyClass(IHTMLTransformation, transformation.ImageRemover)
        verifyClass(IHTMLTransformation, transformation.LinkRemover)
        verifyClass(IHTMLTransformation, transformation.ReviewHistoryRemover)
        verifyClass(IHTMLTransformation, transformation.PageBreaker)

    def testLinkListAdder(self):

        T = transformation.LinkListAdder(html)
        T.transform()
        html2 = str(T)
        self.assertEqual('[1] http://www.heise.de' in html2, True)
        self.assertEqual('[2] http://www.heise.de#anchor' in html2, True)
        self.assertEqual('[3] /foo/bar' in html2, True)
        self.assertEqual('[4] http://foo.com' in html2, True)

    def testGetLinks(self):
        T = transformation.LinkListAdder(html)
        links = T.getLinksInHtml()    
        self.assertEqual(links, ['http://www.heise.de',
                                 'http://www.heise.de#anchor',
                                 '/foo/bar',                  
                                 'http://foo.com',
                                ])

    def testEnumerateLinks(self):
        T = transformation.LinkListAdder(html)
        links = T.enumerateLinks()
        html2 = str(T)
        self.assertEqual('HEISE [1]' in html2, True)
        self.assertEqual('HEISE [2]' in html2, True)
        self.assertEqual('foo bar [3]' in html2, True)
        self.assertEqual('bar [4]' in html2, True)

    def testPageBreaker(self):
        html = """<h1>hello world </h1><div>foo bar</div>\n
        <H1>Chapter 2</h1><div>chapter 2 goes here</div>"""
        T = transformation.PageBreaker(html)
        T.transform()
        result = str(T)
        self.assertEqual(result, '<div class="chapter sp-page"><h1>hello world </h1><div>foo bar</div></div>\n'\
                                 '<div class="chapter"><h1>Chapter 2</h1><div>chapter 2 goes here</div></div>')

    def testLinkRemover(self):
        T = transformation.LinkRemover(html) 
        T.transform()
        result = str(T)
        self.assertEqual('<span>HEISE</span>' in result, True)
        self.assertEqual('<span>Control Panel</span>' in result, True)
        self.assertEqual('<span>foo bar</span>' in result, True)

    def testEmptyElementRemover(self):
        T = transformation.EmptyElementRemover('<div>hello world<div></div><p></p></div>') 
        T.transform()
        result = str(T)
        self.assertEqual(result, '<div>hello world</div>')


    def testLinksToPrinceFootnotes(self):
        T = transformation.LinksToPrinceFootnotes('<a href="http://plone.org">plone.org</a>')
        T.transform()
        result = str(T)
        self.assertEqual(result, '<span class="generated-footnote-text">plone.org<span class="generated-footnote">http://plone.org</span></span>')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TransformationTests))
    return suite

