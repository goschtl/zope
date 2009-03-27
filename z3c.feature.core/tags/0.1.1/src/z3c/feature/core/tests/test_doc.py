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
"""Test Setup.

$Id$
"""
import os
import shutil
import unittest
import tempfile
import logging
import zope.testing.doctest
import zope.component
from zope.configuration import xmlconfig
from z3c.builder.core import testing

def test_suite():
    return unittest.TestSuite((

        zope.testing.doctest.DocFileSuite(
            '../README.txt',
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        zope.testing.doctest.DocFileSuite(
            '../example.txt',
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        zope.testing.doctest.DocFileSuite(
            '../base.txt',
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        zope.testing.doctest.DocFileSuite(
            '../metadata.txt',
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        zope.testing.doctest.DocFileSuite(
            '../python.txt',
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        zope.testing.doctest.DocFileSuite(
            '../unittest.txt',
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        zope.testing.doctest.DocFileSuite(
            '../xml.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        ))
