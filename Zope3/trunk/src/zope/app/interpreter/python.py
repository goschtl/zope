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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Python Code Interpreter

$Id$
"""
import StringIO
import sys

from zope.app.interpreter.interfaces import IInterpreter
from zope.interface import implements
from zope.security.interpreter import RestrictedInterpreter

class PythonInterpreter:

    implements(IInterpreter)

    def evaluate(self, code, globals):
        """See zope.app.interfaces.IInterpreter"""
        tmp = sys.stdout
        sys.stdout = StringIO.StringIO()
        ri = RestrictedInterpreter()
        ri.globals = globals
        try:
            # This used to add a newline for Python 2.2. As far as 
            # I know, we only care about 2.3 and later.
            ri.ri_exec(code)
        finally:
            result = sys.stdout
            sys.stdout = tmp
        return result.getvalue()
        

    def evaluateRawCode(self, code, globals):
        """See zope.app.interfaces.IInterpreter"""
        # Removing probable comments
        if code.strip().startswith('<!--') and code.strip().endswith('-->'):
            code = code.strip()[4:-3]

        # Prepare code.
        lines = code.splitlines()
        lines = filter(lambda l: l.strip() != '', lines)
        code = '\n'.join(lines)
        # This saves us from all indentation issues :)
        if code.startswith(' ') or code.startswith('\t'):
            code = 'if 1 == 1:\n' + code
        return self.evaluate(code, globals)
        

# It's a singelton for now.
PythonInterpreter = PythonInterpreter()
