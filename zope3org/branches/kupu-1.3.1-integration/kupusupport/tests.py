##############################################################################
#
# Copyright (c) 2003-2004 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Zope3 isar sprint sample integration

$Id: $
"""

__docformat__ = "reStructuredText"

import unittest
from zope.testing.doctest import DocTestSuite
from zope.app.tests import placelesssetup  


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocTestSuite('kupusupport.adapters'))
    suite.addTest(DocTestSuite('kupusupport.browser.views'))
    return suite
