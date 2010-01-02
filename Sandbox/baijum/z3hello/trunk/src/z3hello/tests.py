import os.path
import z3c.testsetup
import z3hello
from zope.app.testing.functional import ZCMLLayer


ftesting_zcml = os.path.join(
    os.path.dirname(z3hello.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer',
                            allow_teardown=True)

test_suite = z3c.testsetup.register_all_tests('z3hello')
