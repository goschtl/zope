##############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests

"""
__docformat__ = "reStructuredText"

import unittest

from zope.testing import doctest
import zope.app.testing.functional

from zc.sourcefactory.tests import SourceFactoryLayer

def test_suite():
    suite = unittest.TestSuite()
    token = zope.app.testing.functional.FunctionalDocFileSuite('token.txt')
    token.layer = SourceFactoryLayer
    readme =  zope.app.testing.functional.FunctionalDocFileSuite(
            'README.txt', optionflags=doctest.ELLIPSIS)
    readme.layer = SourceFactoryLayer
    suite.addTest(token)
    suite.addTest(readme)
    return suite
