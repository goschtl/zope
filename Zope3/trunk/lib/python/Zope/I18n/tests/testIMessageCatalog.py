##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""This is an 'abstract' test for the IMessageCatalog interface.

$Id: testIMessageCatalog.py,v 1.2 2002/06/13 16:35:20 srichter Exp $
"""

import unittest
from Interface.Verify import verifyObject
from Zope.I18n.IMessageCatalog import IMessageCatalog


class TestIMessageCatalog(unittest.TestCase):


    # This should be overwritten by every class that inherits this test
    def _getMessageCatalog(self):
        pass
    
    def _getUniqueIndentifier(self):
        pass


    def setUp(self):
        self._catalog = self._getMessageCatalog() 
        assert verifyObject(IMessageCatalog, self._catalog)


    def testGetMessage(self):
        catalog = self._catalog    
        self.assertEqual(catalog.getMessage('short_greeting'), 'Hello!')
        self.assertRaises(KeyError, catalog.getMessage, 'foo')
        

    def testQueryMessage(self):
        catalog = self._catalog    
        self.assertEqual(catalog.queryMessage('short_greeting'), 'Hello!')
        self.assertEqual(catalog.queryMessage('foo'), 'foo')
        self.assertEqual(catalog.queryMessage('foo', 'bar'), 'bar')

        
    def testGetLanguage(self):
        catalog = self._catalog    
        self.assertEqual(catalog.getLanguage(), 'en')


    def testGetDomain(self):
        catalog = self._catalog    
        self.assertEqual(catalog.getDomain(), 'default')


    def testGetIdentifier(self):
        catalog = self._catalog    
        self.assertEqual(catalog.getIdentifier(), self._getUniqueIndentifier())


def test_suite():
    pass
