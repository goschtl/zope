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
"""compile() equivalent that produces restricted code.

Only 'eval' is supported at this time.

$Id$
"""

import compiler.pycodegen

import RestrictedPython.RCompile

import zope.restrictedpython.mutator


def compile(text, filename, mode):
    if mode != "eval":
        raise ValueError("only 'eval' mode is supported")
    gen = RExpression(text, filename)
    gen.compile()
    return gen.getCode()


class RExpression(RestrictedPython.RCompile.RestrictedCompileMode):

    mode = "eval"
    CodeGeneratorClass = compiler.pycodegen.ExpressionCodeGenerator

    def __init__(self, source, filename):
        RestrictedPython.RCompile.RestrictedCompileMode.__init__(
            self, source, filename)
        self.rm = zope.restrictedpython.mutator.RestrictionMutator()
