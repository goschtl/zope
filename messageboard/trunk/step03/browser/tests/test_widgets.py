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
"""HTMLSourceWidget Tests

$Id: test_widgets.py,v 1.1 2003/06/10 14:40:44 srichter Exp $
"""
import unittest
from zope.app.form.browser.tests.test_textareawidget import TextAreaWidgetTest
from book.messageboard.browser.widgets import HTMLSourceWidget
from book.messageboard.fields import HTML

class HTMLSourceWidgetTest(TextAreaWidgetTest):

    _FieldFactory = HTML
    _WidgetFactory = HTMLSourceWidget


    def test_AllowedTagsConvert(self):
        widget = self._widget
        widget.context.allowed_tags=('h1','pre')
        self.assertEqual(u'<h1>Blah</h1>',
                         widget._convert(u'<h1>Blah</h1>')) 
        self.assertEqual(u'<pre>Blah</pre>',
                         widget._convert(u'<pre>Blah</pre>') )
        self.assertEqual(u'<h1><pre>Blah</pre></h1>',
                         widget._convert(u'<h1><pre>Blah</pre></h1>')) 
        self.assertEqual(u'<h1 attr=".">Blah</h1>',
                         widget._convert(u'<h1 attr=".">Blah</h1>')) 

        self.assertEqual(u'Blah',
                         widget._convert(u'<h2>Blah</h2>')) 
        self.assertEqual(u'<pre>Blah</pre>',
                         widget._convert(u'<h2><pre>Blah</pre></h2>')) 
        self.assertEqual(u'Blah',
                         widget._convert(u'<h2 a="b">Blah</h2>')) 


    def test_ForbiddenTagsConvert(self):
        widget = self._widget
        widget.context.forbidden_tags=('h2','pre')

        self.assertEqual(u'<h1>Blah</h1>',
                         widget._convert(u'<h1>Blah</h1>')) 
        self.assertEqual(u'<h1 a="b">Blah</h1>',
                         widget._convert(u'<h1 a="b">Blah</h1>')) 

        self.assertEqual(u'Blah',
                         widget._convert(u'<h2>Blah</h2>')) 
        self.assertEqual(u'Blah',
                         widget._convert(u'<pre>Blah</pre>')) 
        self.assertEqual(u'Blah',
                         widget._convert(u'<h2><pre>Blah</pre></h2>')) 
        self.assertEqual(u'Blah',
                         widget._convert(u'<h2><pre>Blah</pre></h2>')) 
        self.assertEqual(u'<h1>Blah</h1>',
                         widget._convert(u'<h1><pre>Blah</pre></h1>')) 


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(HTMLSourceWidgetTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
