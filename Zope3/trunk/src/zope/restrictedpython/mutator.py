##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Modify AST to include security checks.

RestrictionMutator modifies a tree produced by
compiler.transformer.Transformer, restricting and enhancing the
code in various ways before sending it to pycodegen.

$Revision: 1.13 $
"""

from RestrictedPython.SelectCompiler import ast, OP_ASSIGN, OP_DELETE, OP_APPLY


# The security checks are performed by a set of six functions that
# must be provided by the restricted environment.

_getattr_name = ast.Name("getattr")


class RestrictionMutator:

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.used_names = {}

    def error(self, node, info):
        """Records a security error discovered during compilation."""
        lineno = getattr(node, 'lineno', None)
        if lineno is not None and lineno > 0:
            self.errors.append('Line %d: %s' % (lineno, info))
        else:
            self.errors.append(info)

    def visitGetattr(self, node, walker):
        """Converts attribute access to a function call.

        'foo.bar' becomes 'getattr(foo, "bar")'.

        Also prevents augmented assignment of attributes, which would
        be difficult to support correctly.
        """
        node = walker.defaultVisitNode(node)
        return ast.CallFunc(_getattr_name,
                            [node.expr, ast.Const(node.attrname)])
