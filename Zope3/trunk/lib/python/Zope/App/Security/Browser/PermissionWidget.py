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
"""Widget for selecting permissions.

$Id: PermissionWidget.py,v 1.1 2002/12/21 19:57:30 stevea Exp $
"""

from Zope.App.Forms.Views.Browser.IBrowserWidget import IBrowserWidget
from Zope.App.Forms.Views.Browser import Widget
from Zope.ComponentArchitecture import getService

class BaseWidget:

    def _convert(self, permission_id):
        if not permission_id:
            return None
        service = getService(self.context.context, "Permissions")
        return service.getPermission(permission_id)

    def _unconvert(self, permission):
        if permission is None:
            return None
        return permission.getId()

class SinglePermissionWidget(BaseWidget, Widget.BrowserWidget):    

    def __call__(self):
        search_name = self.name + ".search"
        search_string = self.request.form.get(search_name, '')

        service = getService(self.context.context, "Permissions")
        permissions = list(service.getPermissions())
        permissions.sort(lambda x,y: cmp(x.getId(), y.getId()))
        permissions = map(self._unconvert, permissions)
        if search_string:
            permissions = [permission
                           for permission in permissions
                           if permission.find(search_string)!=-1]
        permissions.sort()

        select_name = self.name
        selected = self._showData()
        
        options = ['<option value=\"\">---select permission---</option>']
        for permission in permissions:
            options.append('<option value="%s"%s>%s</option>'
                           % (permission,
                              permission == selected and ' selected' or '',
                              permission)
                           )
            

        search_field = '<input type="text" name="%s" value=\"%s\">' % (
            search_name, search_string)
        select_field = '<select name="%s">%s</select>'  % (
            select_name, ''.join(options))
        
        HTML = search_field + select_field
        return HTML

class DisplayWidget(BaseWidget, Widget.DisplayWidget):
    pass

    
