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

$Id: permissionwidget.py,v 1.5 2004/03/14 01:11:41 srichter Exp $
"""
from zope.interface import implements
from zope.i18n import translate 

from zope.app import zapi
from zope.app.form.browser import widget
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.security.interfaces import IPermission
from zope.security.checker import CheckerPublic
import zope.app.form.interfaces


class BaseWidget:

    def _convert(self, permission_id):
        if not permission_id:
            # No permission selected
            return None
        
        if type(permission_id) is unicode:
            try:
                permission_id = permission_id.encode('ascii')
            except UnicodeError, v:
                raise ConversionError("Invalid textual data", v)
            
        if permission_id == 'zope.Public':
            permission_id = CheckerPublic

        return permission_id

    def _unconvert(self, permission_id):
        if permission_id is CheckerPublic:
            permission_id = 'zope.Public'
        return permission_id

class SinglePermissionWidget(BaseWidget, widget.BrowserWidget):

    implements(zope.app.form.interfaces.IInputWidget)

    def __call__(self):
        search_name = self.name + ".search"
        search_string = self.request.form.get(search_name, '')

        utils = zapi.getUtilitiesFor(self.context.context, IPermission)
        permissions = [name for name, p in utils]
        permissions.sort()

        if search_string:
            permissions = [permission
                           for permission in permissions
                           if permission.find(search_string)!=-1]

        select_name = self.name
        selected = self._showData()

        sel_perm = _('---select permission---')
        sel_perm = translate(self.context.context, sel_perm,
                             context=self.request)
        
        options = ['<option value=\"\">'+sel_perm+'</option>']
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

class DisplayWidget(BaseWidget, widget.DisplayWidget):
    pass
