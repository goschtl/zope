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
$Id: RestrictedInterpreter.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

import sys

from Proxy import ProxyFactory
from RestrictedBuiltins import RestrictedBuiltins

class RestrictedInterpreter:

    def __init__(self):
        self.globals = {'__builtins__' : RestrictedBuiltins}

    def ri_exec(self, code):
        # what is the type of code?
        exec code in self.globals
