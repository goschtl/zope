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
"""

Revision information:
$Id: interpreter.py,v 1.1 2002/12/31 03:35:13 jim Exp $
"""

import sys

from zope.security.proxy import ProxyFactory
from zope.security.builtins import RestrictedBuiltins

class RestrictedInterpreter:

    def __init__(self):
        self.globals = {'__builtins__' : RestrictedBuiltins}

    def ri_exec(self, code):
        # what is the type of code?
        exec code in self.globals
