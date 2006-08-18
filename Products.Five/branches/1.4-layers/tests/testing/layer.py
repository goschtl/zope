from Testing.ZopeTestCase.utils import setDebugMode
from Testing.ZopeTestCase.layer import Zope2Layer

class ZCMLLayer:
    @classmethod
    def setUp(cls):
        # this keeps five from hiding config errors while toggle debug
        # back on to let PTC perform efficiently
        setDebugMode(1)
        from Products.Five import zcml
        zcml.load_site()
        setDebugMode(0)
        
    @classmethod
    def tearDown(cls):
        from zope.testing.cleanup import cleanUp
        cleanUp()

class FiveLayer(ZCMLLayer, Zope2Layer):
    """3 + 2"""
