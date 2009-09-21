import z3c.testsetup
import os.path
import grokui.base
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(
    os.path.dirname(grokui.base.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__,
                            'GrokUIBaseFunctionalLayer',
                            allow_teardown=True)

test_suite = z3c.testsetup.register_all_tests('grokui.base')
