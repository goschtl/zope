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

Revision information: $Id: Contents.py,v 1.9 2002/11/18 23:52:59 jim Exp $
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.OFS.Container.IContainer import IContainer
from Zope.ComponentArchitecture \
     import queryView, getView, queryAdapter,  getAdapter
from Zope.App.DublinCore.IZopeDublinCore import IZopeDublinCore
from Zope.Event import publishEvent
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.OFS.Container.IZopeContainer import IZopeContainer

class Contents(BrowserView):

    __used_for__ = IContainer

    def _extractContentInfo( self, item ):
        info = { }
        info['id'] = item[0]
        info['object'] = item[1]

        info[ 'url' ] = item[0]

        zmi_icon = queryView(item[1], 'zmi_icon', self.request)
        if zmi_icon is None:
            info['icon'] = None
        else:
            info['icon'] = zmi_icon()

        dc = queryAdapter(item[1], IZopeDublinCore)
        if dc is not None:
            title = dc.title
            if title:
                info['title'] = title

            created = dc.created
            if created is not None:
                info['created'] = created

            modified = dc.modified
            if modified is not None:
                info['modified'] = modified

        return info


    def removeObjects(self, ids):
        """Remove objects specified in a list of object ids"""
        container = self.context
        for id in ids:
            container = getAdapter(container, IZopeContainer)
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
