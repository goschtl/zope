##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test that the package's configure.zcml can be loaded.

$Id$
"""
import unittest

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig


class TestBrowserFormZCML(PlacelessSetup, unittest.TestCase):

    def test_load_zcml(self):
        # XXX Not much of a test.
        xmlconfig.string(
            """<configure xmlns='http://namespaces.zope.org/zope'>
                 <include package='zope.app.component' file='meta.zcml' />
                 <include package='zope.app.publisher.browser'
                          file='meta.zcml' />
            
                 <include package='zope.app.form.browser' />
               </configure>"""
            )


def test_suite():
    return unittest.makeSuite(TestBrowserFormZCML)

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
