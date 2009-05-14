##########################################################################
# zopyx.smartprintng.core 
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


"""
Tests, tests, tests.........
"""

import unittest

from zope.interface.verify import verifyClass
from zopyx.smartprintng.core.interfaces import IImageFetcher
from zopyx.smartprintng.core.adapters import ExternalImageFetcher


class AdapterTests(unittest.TestCase):

    def testInterfaces(self):
        verifyClass(IImageFetcher, ExternalImageFetcher)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AdapterTests))
    return suite

