##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Restricted interpreter.

TODO: This code needs a serious security review!!!

$Id$
"""
from zope.security.builtins import RestrictedBuiltins

class RestrictedInterpreter:

    def __init__(self):
        self.globals = {}
        self.locals = {}

    def ri_exec(self, code):
        """Execute Python code in a restricted environment.

        The value of code can be either source or binary code."""
        self.globals['__builtins__'] = RestrictedBuiltins
        exec code in self.globals, self.locals
