##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Resource License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: app.py 44 2007-02-21 09:43:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks
from zope.app.container.interfaces import IContainer
from zope.app.folder.interfaces import IFolder
from zope.viewlet import viewlet

from z3c.website import interfaces
import z3c.website.layer


class Content(viewlet.ViewletBase):
    """Content tool."""
    res = None

    def items(self):
        if self.res is not None:
            return self.res
        self.res = []
        append = self.res.append
        try:
            if IContainer.providedBy(self.context):
                # get childs if we stay at a container
                context = self.context
            elif IContainer.providedBy(self.context.__parent__):
                # get siblings
                context = self.context.__parent__
            else:
                return []
            # just getting myself access to the site.
            if IFolder.providedBy(context):
                return []
            for item in context.values():
                info = {}
                info['url'] = absoluteURL(item, self.request)
                if hasattr(item, 'title'):
                    info['title'] = item.title
                else:
                    info['title'] = u'undefined'
                append(info)
        except KeyError:
            # site does not exist right now
            pass
        return self.res

    def render(self, *args, **kw):
        """See zope.contentprovider.interfaces.IContentProvider"""
        if len(self.items()) == 0:
            return u''
        if interfaces.ISamples.providedBy(self.context) or \
            interfaces.ISample.providedBy(self.context):
            return u''
        return self.index(*args, **kw)
