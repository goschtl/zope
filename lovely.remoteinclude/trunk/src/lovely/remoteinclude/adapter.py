##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id$
"""
__docformat__ = 'restructuredtext'

from zope.traversing.namespace import view
from interfaces import IIncludeableView
from zope import component

from zope.contentprovider.interfaces import IBeforeUpdateEvent
from zope import component
from zope.security.proxy import removeSecurityProxy


@component.adapter(IIncludeableView, IBeforeUpdateEvent)
def makeInclude(view, ev):
    traversed = removeSecurityProxy(ev.request._last_obj_traversed)
    if traversed.context is view or traversed is view:
        # if we are directly published do not render an include
        return
    inc = component.queryMultiAdapter((view, ev.request),
                                      name="include")
    if inc is not None:
        view = removeSecurityProxy(view)
        view.update = lambda: None
        view.render = inc.__call__


class IncludeViewTraversable(view):

    def traverse(self, name, ignored):
        view = super(IncludeViewTraversable, self).traverse(name,
                                                            ignored)
        if IIncludeableView.providedBy(view):
            inc = component.queryMultiAdapter((view, self.request),
                                              name="include")
            if inc is not None:
                return inc
        return view

