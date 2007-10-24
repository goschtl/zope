##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Functional tests for i18n versions of several content objects.

$Id$
"""

__docformat__ = 'restructuredtext'

import re
import unittest
from zope.testing import renormalizing
from zope.app.testing.functional import FunctionalDocFileSuite
from zope.app.i18nfile.testing import I18nFileLayer


checker = renormalizing.RENormalizing([
    (re.compile(r"HTTP/1\.1 200 .*"), "HTTP/1.1 200 OK"),
    (re.compile(r"HTTP/1\.1 303 .*"), "HTTP/1.1 303 See Other"),
    ])


def test_suite():
    suite = unittest.TestSuite()
    i18nfile = FunctionalDocFileSuite("i18nfile.txt", checker=checker)
    i18nfile.layer = I18nFileLayer
    suite.addTest(i18nfile)
    i18nimage = FunctionalDocFileSuite("i18nimage.txt", checker=checker)
    i18nimage.layer = I18nFileLayer
    suite.addTest(i18nimage)
    return suite
