##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for xmlrpcintrospection

$Id$
"""

from zope.app.testing import functional
from zope.app.xmlrpcintrospection.ftests import setUp, tearDown, checker
from zope.app.xmlrpcintrospection.testing import XmlrpcIntrospectionLayer

def test_suite():
    suite = functional.FunctionalDocFileSuite(
        '../README.txt', setUp=setUp, tearDown=tearDown, checker=checker)
    suite.layer = XmlrpcIntrospectionLayer
    return suite


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')
