
from five.grok.testing import cleanUp, setDebugMode

import five.megrok.z3cpt

def safe_load_site():
    '''Loads entire component architecture (w/ debug mode on).'''
    cleanUp()
    setDebugMode(1)
    import Products.Five.zcml as zcml
    zcml.load_site()
    zcml.load_config('ftesting.zcml', five.megrok.z3cpt)
    setDebugMode(0)

class Layer:

    def setUp(cls):
        '''Sets up the CA by loading etc/site.zcml.'''
        safe_load_site()
    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Cleans up the CA.'''
        cleanUp()
    tearDown = classmethod(tearDown)

GrokFunctionalLayer = Layer
