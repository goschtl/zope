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
"""Test the generic persistent Message Catalog.

$Id: test_messagecatalog.py,v 1.2 2002/12/25 14:13:23 jim Exp $
"""
import unittest

from zope.app.services.translation.messagecatalog import \
     MessageCatalog
from zope.i18n.tests.test_ireadmessagecatalog import TestIReadMessageCatalog
from zope.i18n.tests.test_iwritemessagecatalog import TestIWriteMessageCatalog


class MessageCatalogTest(TestIReadMessageCatalog, TestIWriteMessageCatalog):


    def startUp(self):
        TestIReadMessageCatalog.startUp(self)
        TestIWriteMessageCatalog.startUp(self)


    def _getMessageCatalog(self):
        catalog = MessageCatalog('en', 'default')
        catalog.setMessage('short_greeting', 'Hello!', 0)
        catalog.setMessage('greeting', 'Hello $name, how are you?', 0)
        return catalog

    def _getUniqueIndentifier(self):
        return ('en', 'default')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(MessageCatalogTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
