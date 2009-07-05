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
from zope.tales.expressions import StringExpr, SimpleModuleImporter
from zope.component import queryUtility, queryAdapter, queryMultiAdapter

from interfaces import IPagelet, IPageletType, IPageletContext


class PageletExpression(object):

    def render(self, context, request, view, name):
        modules = SimpleModuleImporter()
        
        pageletName = u''

        # lookup pagelet
        if name:
            splited = name.split(';', 1)
            if len(splited) > 1:
                name, pageletName = splited

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

        contexts = queryAdapter(context, IPageletContext, name)
        if contexts is not None:
            required = [context]
            if type(contexts) in (list, tuple):
                required.extend(contexts)
            else:
                required.append(contexts)
            required.append(request)
            view = queryMultiAdapter(required, iface, pageletName)
        else:
            view = queryMultiAdapter((context, request), iface, pageletName)

        if view is not None:
            try:
                view.update()
                if view.isRedirected:
                    return u''
                return view.render()
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
