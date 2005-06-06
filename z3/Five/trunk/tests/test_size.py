##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Size adapters for testing

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeDocTestSuite, installProduct
installProduct('Five')

from zope.interface import implements
from zope.app.size.interfaces import ISized

class SimpleContentSize(object):
    """Size for ``SimpleContent`` objects."""
    implements(ISized)

    def __init__(self, context):
	self.context = context

    def sizeForSorting(self):
	return ('byte', 42)

    def sizeForDisplay(self):
	return "What is the meaning of life?"

class FancyContentSize(object):
    """Size for ``SimpleContent`` objects."""
    implements(ISized)

    def __init__(self, context):
	self.context = context

    def sizeForSorting(self):
	return ('line', 143)

    def sizeForDisplay(self):
	return "That's not the meaning of life!"

configure_zcml = """
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:five="http://namespaces.zope.org/five">

  <five:sizable class="Products.Five.tests.simplecontent.SimpleContent" />
  <five:sizable class="Products.Five.tests.fancycontent.FancyContent" />

  <adapter
      for="Products.Five.tests.simplecontent.ISimpleContent"
      provides="zope.app.size.interfaces.ISized"
      factory="Products.Five.tests.test_size.SimpleContentSize"
      />
  <adapter
      for="Products.Five.tests.fancycontent.IFancyContent"
      provides="zope.app.size.interfaces.ISized"
      factory="Products.Five.tests.test_size.FancyContentSize"
      />

</configure>
"""

def setUpSize(self):
    from Products.Five import zcml
    zcml.load_string(configure_zcml)

def test_size():
    """Test size adapters

      >>> from Products.Five.tests.simplecontent import manage_addSimpleContent
      >>> from Products.Five.tests.fancycontent import manage_addFancyContent

    We have registered an ``ISized`` adapter for SimpleContent:

      >>> n = manage_addSimpleContent(self.folder, 'simple', 'Simple')
      >>> self.folder.simple.get_size()
      42

    Fancy content already has a ``get_size`` method

      >>> n = manage_addFancyContent(self.folder, 'fancy', 'Fancy')
      >>> self.folder.fancy.get_size()
      43
    """

def test_suite():
    return unittest.TestSuite((
            ZopeDocTestSuite(setUp=setUpSize),
            ))

if __name__ == '__main__':
    framework()
