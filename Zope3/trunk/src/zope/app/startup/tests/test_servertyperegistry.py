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
"""
I do not think it is necessary to do the entire SimpleRegistry tests again.
Instead we will test whether the module in itself works.

$Id: test_servertyperegistry.py,v 1.4 2003/06/06 19:42:57 stevea Exp $
"""

import unittest
from zope.app.startup.servertyperegistry import \
     registerServerType, getServerType
from zope.app.startup.servertype import IServerType
from zope.interface import implements


class ServerType:
    """ServerType Stub."""

    implements(IServerType)


class Test(unittest.TestCase):


    def testRegistry(self):

        server = ServerType()

        registerServerType('server', server)
        self.assertEqual(getServerType('server'), server)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
