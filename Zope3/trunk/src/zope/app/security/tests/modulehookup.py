##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Preliminaries to hookup a test suite with the external TestModule.

This is necessary because the test framework interferes with seeing changes in
the running modules via the module namespace.  This enables having some
subject classes, instances, permissions, etc, that don't live in the test
modules, themselves."""

from zope.interface import Interface

PREFIX = "zope.app.security.tests.module."
import zope.app.security.tests.module
from zope.app.security.tests import module as TestModule
TestModule.test_class = None

class I(Interface):
    def m1():
        pass
    def m2():
        pass

class I2(I):
    def m4():
        pass


TestModule.I = I
TestModule.I2 = I2

template_bracket = """<zopeConfigure
   xmlns="http://namespaces.zope.org/zope" >
   %s
</zopeConfigure>"""
