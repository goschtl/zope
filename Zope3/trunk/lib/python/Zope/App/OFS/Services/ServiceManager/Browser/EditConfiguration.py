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
$Id: EditConfiguration.py,v 1.4 2002/12/06 14:16:31 gvanrossum Exp $
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
        if 'add_submit' in self.request:
            self.request.response.redirect('+')
            return ''

        if 'keys' in self.request:
            k = self.request['keys']
        else:
            k = []

        msg = 'You must select at least one item to use this action'

        if 'remove_submit' in self.request:
            if not k: return msg
            self.remove_objects(k)
        elif 'top_submit' in self.request:
            if not k: return msg
            self.context.moveTop(k)
        elif 'bottom_submit' in self.request:
            if not k: return msg
            self.context.moveBottom(k)
        elif 'up_submit' in self.request:
            if not k: return msg
            self.context.moveUp(k)
        elif 'down_submit' in self.request:
            if not k: return msg
            self.context.moveDown(k)

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

