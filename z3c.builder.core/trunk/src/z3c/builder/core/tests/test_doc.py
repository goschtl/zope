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
import re
import shutil
import sys
import unittest
import tempfile
import logging
import subprocess
import tempfile
import zope.component
from zope.configuration import xmlconfig
from zope.testing import renormalizing, doctest

from z3c.builder.core import base, testing

def fullSetUp(test):
    testing.buildSetUp(test)
    testing.loggerSetUp(test)

def fullTearDown(test):
    testing.buildTearDown(test)
    testing.loggerTearDown(test)

def test_suite():
    checker = renormalizing.RENormalizing([
       (re.compile(
            '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}'),
            '<DATETIME>'),
       (re.compile(
            '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
            '<UUID>'),
       ])

    return unittest.TestSuite((

        doctest.DocFileSuite(
            '../README.txt',
            setUp=fullSetUp, tearDown=fullTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),

        doctest.DocFileSuite(
            '../project.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),

        doctest.DocFileSuite(
            '../python.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),

        doctest.DocFileSuite(
            '../setup.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),

        doctest.DocFileSuite(
            '../buildout.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),

        doctest.DocFileSuite(
            '../zcml.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),

        doctest.DocFileSuite(
            '../form.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),

        doctest.DocFileSuite(
            '../example.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_NDIFF,
            checker=checker),

        ))
