##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for PropertiesTool module.

$Id$
"""

import unittest
import Testing


class PropertiesToolTests(unittest.TestCase):

    def test_z2interfaces(self):
        from Interface.Verify import verifyClass
        from Products.CMFCore.interfaces.portal_properties \
                import portal_properties as IPropertiesTool
        from Products.CMFDefault.PropertiesTool import PropertiesTool

        verifyClass(IPropertiesTool, PropertiesTool)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCore.interfaces import IPropertiesTool
        from Products.CMFDefault.PropertiesTool import PropertiesTool

        verifyClass(IPropertiesTool, PropertiesTool)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PropertiesToolTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
