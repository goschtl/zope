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
""" 'pagelet' tales expression registrations

$Id: tales.py 2720 2008-08-25 11:15:10Z fafhrd91 $
"""
import logging, sys
from zope.component import queryUtility, queryAdapter, queryMultiAdapter
from zope.error.interfaces import IErrorReportingUtility
from zope.tales.expressions import StringExpr, SimpleModuleImporter

from pagelet import queryPagelet
from interfaces import IPagelet, IPageletType, IPageletContext


class PageletExpression(object):

    def render(self, context, request, view, name):
        try:
            pagelet = queryPagelet(context, request, name)
            if pagelet is not None:
                return pagelet.updateAndRender()
        except:
            errUtility = queryUtility(IErrorReportingUtility)
            if errUtility is not None:
                errUtility.raising(sys.exc_info(), request)

        return u''


class TALESPageletExpression(StringExpr, PageletExpression):

    def __call__(self, econtext):
        name = super(TALESPageletExpression, self).__call__(econtext)

        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        return self.render(context, request, view, name)
