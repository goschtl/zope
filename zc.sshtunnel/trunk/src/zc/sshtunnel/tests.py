##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""\
Test harness for zc.sshtunnel.

"""
__docformat__ = "reStructuredText"

import unittest

from zope.testing import doctest
from zope.testing import renormalizing

import zc.buildout.testing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop("zc.sshtunnel", test)
    zc.buildout.testing.install("zope.testing", test)


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            "README.txt",
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.ELLIPSIS,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path])
            ),
        ])
