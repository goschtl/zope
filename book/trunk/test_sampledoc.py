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
"""Code for the Cookbook's Doc Tests Recipe

$Id: test_sample.py,v 1.1.1.1 2004/02/18 18:07:06 srichter Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite

class Sample(object):
    """A trivial Sample object.

    Examples::

      >>> sample = Sample()

      Here you can see how the 'title' attribute works.

      >>> print sample.title
      None
      >>> sample.title = 'Title'
      >>> print sample.title
      Title

      The description is implemented using a accessor and mutator method

      >>> sample.getDescription()
      ''
      >>> sample.setDescription('Hello World')
      >>> sample.getDescription()
      'Hello World'
      >>> sample.setDescription(u'Hello World')
      >>> sample.getDescription()
      u'Hello World'

      'setDescription()' only accepts regular and unicode strings

      >>> sample.setDescription(None)
      Traceback (most recent call last):
        File "<stdin>", line 1, in ?
        File "test_sample.py", line 31, in setDescription
          assert isinstance(value, (str, unicode)) 
      AssertionError
    """

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


def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
