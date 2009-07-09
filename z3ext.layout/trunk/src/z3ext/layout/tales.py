##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
from datetime import datetime
import logging, sys
from zope.tales.expressions import StringExpr, SimpleModuleImporter
from zope.component import queryUtility, queryAdapter, queryMultiAdapter

from pagelet import queryPagelet
from interfaces import IPagelet, IPageletType, IPageletContext


class PageletExpression(object):

    def render(self, context, request, view, name):
        try:
            pagelet = queryPagelet(context, request, name)
            if pagelet is not None:
                dt = datetime.now()
                rendered = pagelet.updateAndRender()

                td = datetime.now() - dt
                secs = (td.days*86400+td.seconds) + (0.000001*td.microseconds)
                print >>sys.stderr, 'pagelet:      ', secs, name
  
                return rendered
        except Exception, err:
            log = logging.getLogger('z3ext.layout')
            log.exception(err)

        return u''


class TALESPageletExpression(StringExpr, PageletExpression):

    def __call__(self, econtext):
        name = super(TALESPageletExpression, self).__call__(econtext)

        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        return self.render(context, request, view, name)
