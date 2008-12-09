##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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

import grok
import unittest
from zope.publisher.browser import TestRequest
from zope import component
from megrok.genshi import components

class Mammoth(grok.Model):
    pass

class CavePainting(grok.View):
    pass

class Static(grok.View):
    pass

class Gatherer(grok.View):
    pass

class Food(grok.View):
    
    text = "ME GROK EAT MAMMOTH!"
    
    def me_do(self):
        return self.text

class Hunter(grok.View):
    
    game = "MAMMOTH!"

class Inline(grok.View):
    pass

inline = components.GenshiMarkupTemplate("<html><body>ME GROK HAS INLINES!</body></html>")


class GenshiTemplateTests(unittest.TestCase):
    
    def test_templatedir(self):
        # Templates can be found in a directory with the same name as the module:
      
        manfred = Mammoth()
        request = TestRequest()
        view = component.getMultiAdapter((manfred, request), name='cavepainting')
        self.assertEquals(view(), """<html>
<body>
A cave painting.
</body>
</html>""")
        
    def test_view_access(self):
        # A template can access variables like "view" and it's 
        # methods and attributes.
        manfred = Mammoth()
        request = TestRequest()
        view = component.getMultiAdapter((manfred, request), name='food')
        self.assertEquals(view(), """<html>
<body>
ME GROK EAT MAMMOTH!
</body>
</html>""")
    
    def test_static(self):
        # The URL of static resources can be gotten from the static variable.
        manfred = Mammoth()
        request = TestRequest()
        view = component.getMultiAdapter((manfred, request), name='static')
        html = view()
        self.assert_('@@/megrok.genshi.tests/test.css' in html)

    def test_snippet(self):
        manfred = Mammoth()
        request = TestRequest()
        view = component.getMultiAdapter((manfred, request), name='food')
        view.text = "ME GROK EAT <MAMMOTH>!"
        html = view()
        self.assert_('ME GROK EAT <MAMMOTH>!' in html)

    def test_xinclude(self):
        manfred = Mammoth()
        request = TestRequest()
        view = component.getMultiAdapter((manfred, request), name='gatherer')
        html = view()
        self.assert_('Lovely blueberries!' in html)

    def test_texttemplate(self):
        manfred = Mammoth()
        request = TestRequest()
        view = component.getMultiAdapter((manfred, request), name='hunter')
        text = view()
        self.assertEquals(text, 'ME GROK HUNT MAMMOTH!!')

    def test_inlinetemplate(self):
        manfred = Mammoth()
        request = TestRequest()
        view = component.getMultiAdapter((manfred, request), name='inline')
        html = view()
        self.assert_('ME GROK HAS INLINES!' in html)
        

def test_suite():
    from megrok.genshi.tests import FunctionalLayer
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GenshiTemplateTests))
    suite.layer = FunctionalLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
