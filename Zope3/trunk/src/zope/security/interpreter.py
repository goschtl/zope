##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Restricted interpreter.

XXX This code is not used!  Before using it, a serious security review
should be undertaken.

XXX (SR) Yes the code is used for the inline Python support. As far as I can
tell the security works well, as I had to make all sorts of security
declarations to make it work. 

$Id: interpreter.py,v 1.5 2004/02/20 20:42:12 srichter Exp $
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
