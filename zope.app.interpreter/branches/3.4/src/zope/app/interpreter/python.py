##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Python Code Interpreter

$Id$
"""
__docformat__ = 'restructuredtext'

from StringIO import StringIO

from zope.app.interpreter.interfaces import IInterpreter
from zope.interface import implements
from zope.security.untrustedpython.interpreter import exec_src

class PythonInterpreter(object):

    implements(IInterpreter)

    def evaluate(self, code, globals):
        """See `zope.app.interfaces.IInterpreter`"""
        tmp = StringIO()
        globals['untrusted_output'] = tmp
        if isinstance(code, basestring):
            exec_src(code, globals,
                     {}, # we don't want to get local assignments saved.
                     )
        else:
            # TODO: There are no tests for this branch
            code.exec_(globals,
                       {}, # we don't want to get local assignments saved.
                       )

        return tmp.getvalue()


    def evaluateRawCode(self, code, globals):
        """See `zope.app.interfaces.IInterpreter`"""
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
