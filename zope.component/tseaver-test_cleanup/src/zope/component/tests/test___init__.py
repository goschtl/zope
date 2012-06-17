##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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

import unittest

class PackageAPITests(unittest.TestCase):

    def test_module_conforms_to_IComponentArchitecture(self):
        from zope.interface.verify import verifyObject
        from zope.component.interfaces import IComponentArchitecture
        import zope.component as zc
        verifyObject(IComponentArchitecture, zc)

    def test_module_conforms_to_IComponentRegistrationConvenience(self):
        from zope.interface.verify import verifyObject
        from zope.component.interfaces import IComponentRegistrationConvenience
        import zope.component as zc
        verifyObject(IComponentRegistrationConvenience, zc)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PackageAPITests),
    ))
