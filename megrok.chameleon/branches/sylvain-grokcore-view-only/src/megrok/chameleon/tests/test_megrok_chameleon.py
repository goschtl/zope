import z3c.testsetup
from megrok.chameleon.tests import FunctionalLayer

test_suite = z3c.testsetup.register_all_tests('megrok.chameleon',
                                              layer=FunctionalLayer)
