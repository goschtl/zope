##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

Revision information: $Id: contents.py,v 1.4 2002/12/27 15:22:50 stevea Exp $
"""
from zope.app.interfaces.container import IContainer, IZopeContainer
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.size import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.component import queryView, queryAdapter,  getAdapter
from zope.publisher.browser import BrowserView


class Contents(BrowserView):

    __used_for__ = IContainer

    def _extractContentInfo(self, item):
        id, obj = item
        info = {}
        info['id'] = id
        info['object'] = obj

        info['url'] = id

        zmi_icon = queryView(obj, 'zmi_icon', self.request)
        if zmi_icon is None:
            info['icon'] = None
        else:
            info['icon'] = zmi_icon()

        dc = queryAdapter(obj, IZopeDublinCore)
        if dc is not None:
            title = dc.title
            if title:
                info['title'] = title
            
            created = dc.created
            if created is not None:
                info['created'] = formatTime(created)

            modified = dc.modified
            if modified is not None:
                info['modified'] = formatTime(modified)

        sized_adapter = queryAdapter(obj, ISized)
        if sized_adapter is not None:
            info['size'] = sized_adapter
        return info


    def removeObjects(self, ids):
        """Remove objects specified in a list of object ids"""
        container = getAdapter(self.context, IZopeContainer)
        for id in ids:
            container.__delitem__(id)

        self.request.response.redirect('@@contents.html')

    def listContentInfo(self):
        return map(self._extractContentInfo, self.context.items())

    contents = ViewPageTemplateFile('main.pt')
    contentsMacros = contents

    _index = ViewPageTemplateFile('index.pt')

    def index(self):
        if 'index.html' in self.context:
            self.request.response.redirect('index.html')
            return ''

        return self._index()

# Below is prime material for localization.
# We are a touchpoint that should contact the personalization
# service so that users can see datetime and decimals

def formatTime(in_date):
    format='%m/%d/%Y'
    undefined=u'N/A'
    if hasattr(in_date, 'strftime'):
        return in_date.strftime(format)
    return undefined
