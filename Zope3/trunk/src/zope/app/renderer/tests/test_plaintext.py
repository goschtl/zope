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
"""Plain Text Tests - PlainText Source, HTML Renderer

$Id: test_plaintext.py,v 1.1 2003/07/31 17:59:41 srichter Exp $
"""
import unittest

from zope.publisher.browser import TestRequest

from zope.app.interfaces.renderer import IPlainTextSource, IHTMLRenderer
from zope.app.renderer.plaintext import \
     PlainTextSource, PlainTextToHTMLRenderer


class PlainTextTest(unittest.TestCase):

    def setUp(self):
        self._source = PlainTextSource(u'This is source.')

    def test_Interface(self):
        self.failUnless(IPlainTextSource.isImplementedBy(self._source))

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
        self._source = PlainTextSource(u'This is source.\n')
        self._renderer = PlainTextToHTMLRenderer(self._source, TestRequest())

    def test_Interface(self):
        self.failUnless(IHTMLRenderer.isImplementedBy(self._renderer))

    def test_render(self):
        self.assertEqual('This is source.<br/>\n', self._renderer.render(None))
        comment = self._source.createComment('This is a Comment.', 1,
                                             'srichter',
                                             '04/12/2003 12:00:00')
        self._renderer.context = PlainTextSource(self._source+comment)

        self.assertEqual(rendered_source_comment, self._renderer.render(None))
        

comment = '''

Comment #2 by srichter (04/12/2003 12:00:00)
This is a Comment.'''

first_comment = '''
----------

Comment #1 by srichter (04/12/2003 12:00:00)
This is a Comment.'''

rendered_source_comment = '''This is source.<br/>
<br/>
<hr class="comments" size="1" NOSHADE>
<br/>
Comment #1 by srichter (04/12/2003 12:00:00)<br/>
This is a Comment.'''

    
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PlainTextTest),
        unittest.makeSuite(HTMLRendererTest),
        ))

if __name__ == '__main__':
    unittest.main()
