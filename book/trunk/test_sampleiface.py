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
"""Demonstration of writing unit tests for interfaces

$Id: test_sampleiface.py,v 1.1.1.1 2004/02/18 18:07:00 srichter Exp $
"""
import unittest
from zope.interface import implements, Interface, Attribute
from zope.interface.verify import verifyObject

class ISample(Interface):
    """This is a Sample."""

    title = Attribute('The title of the sample')

    def setDescription(value):
        """Set the description of the Sample.

        Only regular and unicode values should be accepted.
        """

    def getDescription():
        """Return the value of the description."""


class Sample1(object):
    """A trivial ISample implementation."""

    implements(ISample)

    # See ISample
    title = None

    def __init__(self):
        """Create objects."""
        self._description = ''

    def setDescription(self, value):
        """See ISample"""
        assert isinstance(value, (str, unicode)) 
        self._description = value

    def getDescription(self):
        """See ISample"""
        return self._description


class Sample2(object):
    """A trivial ISample implementation."""

    implements(ISample)

    def __init__(self):
        """Create objects."""
        self.__desc = ''
        self.__title = None

    def getTitle(self):
        return self.__title

    def setTitle(self, value):
        self.__title = value

    def setDescription(self, value):
        """See ISample"""
        assert isinstance(value, (str, unicode)) 
        self.__desc = value

    def getDescription(self):
        """See ISample"""
        return self.__desc

    description = property(getDescription, setDescription)

    # See ISample
    title = property(getTitle, setTitle)


class TestISample(unittest.TestCase):
    """Test the ISample interface"""

    def makeTestObject(self):
        """Returns an ISample instance"""
        raise NotImplemented()

    def test_verifyInterfaceImplementation(self):
        self.assert_(verifyObject(ISample, self.makeTestObject()))

    def test_title(self):
        sample = self.makeTestObject()
        self.assertEqual(sample.title, None)
        sample.title = 'Sample Title'
        self.assertEqual(sample.title, 'Sample Title')

    def test_setgetDescription(self):
        sample = self.makeTestObject()
        self.assertEqual(sample.getDescription(), '')
        sample.setDescription('Description')
        self.assertEqual(sample.getDescription(), 'Description')
        self.assertRaises(AssertionError, sample.setDescription, None)


class TestSample1(TestISample):

    def makeTestObject(self):
        return Sample1()

    # Sample1-specific tests are here


class TestSample2(TestISample):

    def makeTestObject(self):
        return Sample2()

    # Sample2-specific tests are here


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSample1),
        unittest.makeSuite(TestSample2)
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
