##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Structured Text Tests - StructuredText Source, HTML Renderer

$Id: test_stx.py,v 1.2 2004/02/19 19:56:53 philikon Exp $
"""
import unittest

from zope.publisher.browser import TestRequest

from zope.app.interfaces.renderer import IStructuredTextSource, IHTMLRenderer
from zope.app.renderer.stx import StructuredTextSource, StructuredTextToHTMLRenderer

class StructuredTextTest(unittest.TestCase):

    def setUp(self):
        self._source = StructuredTextSource(u'This\n is source.')

    def test_Interface(self):
        self.failUnless(IStructuredTextSource.isImplementedBy(self._source))

    def test_createComment(self):
        self.assertEqual(comment,
                         self._source.createComment('This is a Comment.', 2,
                                                    'srichter',
                                                    '04/12/2003 12:00:00'))
        self.assertEqual(first_comment,
                         self._source.createComment('This is a Comment.', 1,
                                                    'srichter',
                                                    '04/12/2003 12:00:00'))


class HTMLRendererTest(unittest.TestCase):

    def setUp(self):
        self._source = StructuredTextSource(u'This is source.\n')
        self._renderer = StructuredTextToHTMLRenderer(self._source,
                                                      TestRequest())

    def test_Interface(self):
        self.failUnless(IHTMLRenderer.isImplementedBy(self._renderer))

    def test_render(self):
        self.assertEqual('<p>This is source.</p>\n',
                         self._renderer.render(None))
        comment = self._source.createComment('This is a Comment.', 1,
                                             'srichter',
                                             '04/12/2003 12:00:00')
        self._renderer.context = StructuredTextSource(self._source+comment)
        self.assertEqual(rendered_source_comment, self._renderer.render(None))
        

comment = '''

Comment #2 by **srichter** (04/12/2003 12:00:00)

This is a Comment.'''

first_comment = '''

----------

Comment #1 by **srichter** (04/12/2003 12:00:00)

This is a Comment.'''

rendered_source_comment = '''<p>This is source.</p>
<hr class="comments" size="1" NOSHADE>
<p>Comment #1 by <strong>srichter</strong> (04/12/2003 12:00:00)</p>
<p>This is a Comment.</p>
'''

    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StructuredTextTest))
    suite.addTest(unittest.makeSuite(HTMLRendererTest))
    return suite

if __name__ == '__main__':
    unittest.main()
