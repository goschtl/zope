import grok
import re
import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest, cleanup, renormalizing
import zope.component.eventtesting
from zope.publisher.browser import TestRequest
from zope import component


class Mammoth(grok.Model):
    pass

class CavePainting(grok.View):
    pass

class Static(grok.View):
    pass

class Food(grok.View):
    
    text = "ME GROK EAT MAMMOTH!"
    
    def me_do(self):
        return self.text


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
        

def test_suite():
    from megrok.genshi.tests import FunctionalLayer
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GenshiTemplateTests))
    suite.layer = FunctionalLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
