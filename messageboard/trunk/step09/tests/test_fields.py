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
"""Message Board Tests

$Id: test_fields.py,v 1.1 2003/06/10 14:40:45 srichter Exp $
"""
import unittest
from zope.schema.tests.test_strfield import TextTest

from book.messageboard.fields import HTML, ForbiddenTags

class HTMLTest(TextTest):

    _Field_Factory = HTML

    def test_AllowedTagsHTMLValidate(self):
        html = self._Field_Factory(allowed_tags=('h1','pre'))
        html.validate(u'<h1>Blah</h1>') 
        html.validate(u'<pre>Blah</pre>') 
        html.validate(u'<h1><pre>Blah</pre></h1>') 
        html.validate(u'<h1 style="..."><pre>Blah</pre></h1>') 
        html.validate(u'<h1 style="..."><pre f="">Blah</pre></h1>') 

        self.assertRaises(ForbiddenTags, html.validate,
                          u'<h2>Foo</h2>')
        self.assertRaises(ForbiddenTags, html.validate,
                          u'<h2><pre>Foo</pre></h2>')
        self.assertRaises(ForbiddenTags, html.validate,
                          u'<h2 attr="blah">Foo</h2>')


    def test_ForbiddenTagsHTMLValidate(self):
        html = self._Field_Factory(forbidden_tags=('h2','pre'))
        html.validate(u'<h1>Blah</h1>') 
        html.validate(u'<h1 style="...">Blah</h1>') 
        html.validate(u'<h1 style="..."><div>Blah</div></h1>') 
        html.validate(u'<h1 style="..."><div f="">Blah</div></h1>') 

        self.assertRaises(ForbiddenTags, html.validate,
                          u'<h2>Foo</h2>')
        self.assertRaises(ForbiddenTags, html.validate,
                          u'<h2><div>Foo</div></h2>')
        self.assertRaises(ForbiddenTags, html.validate,
                          u'<h2 attr="blah">Foo</h2>')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(HTMLTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
