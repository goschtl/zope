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

$Id: python.py,v 1.3 2003/11/04 04:04:27 jeremy Exp $
"""
import StringIO
import sys

from zope.app.interfaces.interpreter import IInterpreter
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
            # The newline character is for Python 2.2 :(
            ri.ri_exec(code+'\n')
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
        lines = code.split('\n')
        lines = filter(lambda l: l.strip() != '', lines)
        code = '\n'.join(lines)
        # This saves us from all indentation issues :)
        if code.startswith(' ') or code.startswith('\t'):
            code = 'if 1 == 1:\n' + code
        return self.evaluate(code, globals)
        

# It's a singelton for now.
PythonInterpreter = PythonInterpreter()
