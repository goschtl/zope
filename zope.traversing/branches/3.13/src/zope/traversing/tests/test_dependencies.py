import unittest

import zope.component
from zope.configuration.xmlconfig import XMLConfig
from zope.publisher.browser import TestRequest

from zope.traversing.interfaces import ITraversable


class ZCMLDependencies(unittest.TestCase):

    def test_zcml_can_load_with_only_zope_component_meta(self):
        import zope.component
        XMLConfig('meta.zcml', zope.component)()

        import zope.traversing
        XMLConfig('configure.zcml', zope.traversing)()

        request = TestRequest()
        res = zope.component.getMultiAdapter(
            (self, request), ITraversable, 'lang')
        import zope.traversing.namespace
        self.failUnless(isinstance(res, zope.traversing.namespace.lang))
        self.failUnless(res.context is self)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZCMLDependencies))
    return suite


if __name__ == '__main__':
    unittest.main()
