##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: EditConfiguration.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getView, getAdapter
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.OFS.Container.IZopeContainer import IZopeContainer

class EditConfiguration(BrowserView):
    """Adding component for service containers
    """

    menu_id = "add_component"

    def __init__(self, context, request):
        self.request = request
        self.context = context

    def action(self):
        """Perform actions depending on user input.

        
        """
        if 'keys' in self.request:
            k = self.request['keys']

        if 'add_submit' in self.request:
            self.request.response.redirect('+')
        elif 'remove_submit' in self.request:
            self.remove_objects(k)
        elif 'top_submit' in self.request:
            self.context.arrange_object(k[0], 'top')
        elif 'bottom_submit' in self.request:
            self.context.arrange_object(k[0],'bottom')
        elif 'up_submit' in self.request:
            self.context.arrange_object(k[0],'up')
        elif 'down_submit' in self.request:
            self.context.arrange_object(k[0],'down')

        return ''

    def remove_objects(self, key_list):
        """Remove the directives from the container.
        """
        container = getAdapter(self.context, IZopeContainer)
        for item in key_list:
            del container[item]
            
    def configInfo(self):
        """Render View for each direcitves.
        """
        r = []
        for name, directive in self.context.items():
            d = ContextWrapper(directive, self.context, name = name)
            view = getView(d, 'ItemEdit', self.request)
            view.setPrefix('config'+str(name))
            r.append({'key': name, 'view': view})
        return r

__doc__ = EditConfiguration.__doc__ + __doc__

