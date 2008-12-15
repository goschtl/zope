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
import logging, sys
from zope.component import queryUtility
from zope.component import queryMultiAdapter
from zope.tales.expressions import StringExpr

from interfaces import IPagelet, IPageletType


class TALESPageletExpression(StringExpr):

    def __call__(self, econtext):
        name = super(TALESPageletExpression, self).__call__(econtext)

        context = econtext.vars['context']
        request = econtext.vars['request']
        modules = econtext.vars['modules']

        # lookup pagelet
        if name:
            iface = queryUtility(IPageletType, name)
            if iface is None:
                try:
                    iface, iname = name.rsplit('.', 1)
                    iface = getattr(modules[iface], iname)
                except Exception, err:
                    log = logging.getLogger('z3ext.layout')
                    log.exception(err)
                    return u''
        else:
            iface = IPagelet

        if iface.providedBy(context):
            return context.render()

        try:
            view = queryMultiAdapter((context, request), iface)
            if view is not None:
                view.update()
                if view.isRedirected:
                    return u''
                return view.render()
        except Exception, err:
            log = logging.getLogger('z3ext.layout')
            log.exception(err)

        return u''
