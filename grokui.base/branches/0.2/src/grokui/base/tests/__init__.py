import os.path
from zope.app.testing import functional

ftesting_zcml = os.path.join(
    os.path.dirname(__file__), 'ftesting.zcml')

FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'GrokUIBaseFunctionalLayer', allow_teardown=True)
