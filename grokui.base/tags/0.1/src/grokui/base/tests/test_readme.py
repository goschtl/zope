# -*- coding: utf-8 -*-

import unittest
from grokui.base import tests
from zope.testing import doctest
from zope.app.testing import functional
from grokui.base.tests import FunctionalLayer


def test_suite():
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite('../README.txt')
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
