##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import re
from chameleon.core import types
from chameleon.zpt import expressions

from tales import PageletExpression


class PageletTraverser(PageletExpression):

    __call__ = PageletExpression.render


class PageletTranslator(expressions.ExpressionTranslator):
    provider_regex = re.compile(r'^[A-Za-z][A-Za-z0-9_\.-;:]*$')

    symbol = '_get_z3ext_pagelet'
    pagelet_traverser = PageletTraverser()

    def translate(self, string, escape=None):
        if self.provider_regex.match(string) is None:
            raise SyntaxError(
                "%s is not a valid content provider name." % string)

        value = types.value("%s(context, request, view, '%s')" % \
                                (self.symbol, string))
        value.symbol_mapping[self.symbol] = self.pagelet_traverser
        return value
