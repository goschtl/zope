import re
import z3c.recipe.compattest.testing
from zope.testing import renormalizing

def test_suite():
    return z3c.recipe.compattest.testing.DocFileSuite(
        'README.txt', 'runner.txt')
