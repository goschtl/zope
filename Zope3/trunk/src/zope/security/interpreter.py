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

$Id: interpreter.py,v 1.2 2003/03/10 16:48:48 gvanrossum Exp $
"""

from zope.security.builtins import RestrictedBuiltins

class RestrictedInterpreter:

    def __init__(self):
        self.globals = {}

    def ri_exec(self, code):
        # XXX What is the type of code?
        self.globals['__builtins__'] = RestrictedBuiltins
        exec code in self.globals
