##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Code for the Zope 3 Book's Unit Tests Chapter

$Id$
"""
import unittest

class Sample(object):
    """A trivial Sample object."""

    title = None

    def __init__(self):
        """Initialize object."""
        self._description = ''

    def setDescription(self, value):
        """Change the value of the description."""
        assert isinstance(value, (str, unicode)) 
        self._description = value

    def getDescription(self):
        """Change the value of the description."""
        return self._description


class SampleTest(unittest.TestCase):
    """Test the Sample class"""

    def test_title(self):
        sample = Sample()
        self.assertEqual(sample.title, None)
        sample.title = 'Sample Title'
        self.assertEqual(sample.title, 'Sample Title')

    def test_getDescription(self):
        sample = Sample()
        self.assertEqual(sample.getDescription(), '')
        sample._description = "Description"
        self.assertEqual(sample.getDescription(), 'Description')
        
    def test_setDescription(self):
        sample = Sample()
        self.assertEqual(sample._description, '')
        sample.setDescription('Description')
        self.assertEqual(sample._description, 'Description')
        sample.setDescription(u'Description2')
        self.assertEqual(sample._description, u'Description2')
        self.assertRaises(AssertionError, sample.setDescription, None)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SampleTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
