import z3c.testsetup
import zope.testing.doctest
from megrok.chameleon.tests import FunctionalLayer

flags = (zope.testing.doctest.ELLIPSIS |
         zope.testing.doctest.NORMALIZE_WHITESPACE)

test_suite = z3c.testsetup.register_all_tests('megrok.chameleon',
                                              optionflags=flags,
                                              layer=FunctionalLayer)
