# *-* coding: iso-8859-15 *-*

"""
Tests
"""

import unittest
import util


class UtilityTests(unittest.TestCase):

    def testIsAscii(self):

        self.assertEqual(util.isASCII('foo'), True)
        self.assertEqual(util.isASCII(u'foo'), True)
        self.assertEqual(util.isASCII('üöä'), False)
        self.assertEqual(util.isASCII(u'üöä'), False)
        self.assertRaises(TypeError, util.isASCII, 2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UtilityTests))
    return suite

