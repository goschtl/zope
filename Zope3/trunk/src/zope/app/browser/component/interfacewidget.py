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
"""These are the interfaces for the common fields.

$Id: interfacewidget.py,v 1.2 2002/12/25 14:12:28 jim Exp $
"""

from zope.interface import Interface
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.browser.form.widget import BrowserWidget, DisplayWidget
from zope.component import getService
from zope.exceptions import NotFoundError
from zope.schema.interfaces import ValidationError

class BaseWidget:

    def _convert(self, name):
        if not name:
            return None
        service = getService(self.context.context, "Interfaces")
        return service.getInterface(name)

    def _unconvert(self, interface):
        if interface is None:
            return interface
        return interface.__module__ + '.' + interface.__name__

class SingleInterfaceWidget(BaseWidget, BrowserWidget):

    def __call__(self):
        search_name = self.name + ".search"
        search_string = self.request.form.get(search_name, '')

        field = self.context
        service = getService(field.context, "Interfaces")
        base = field.type
        if base == Interface:
            base=None
        interfaces = list(service.searchInterface(search_string, base=base))
        interfaces.sort()
        interfaces = map(self._unconvert, interfaces)

        select_name = self.name
        selected = self._showData()

        options = ['<option value=\"\">---select interface---</option>']
        for interface in interfaces:
            options.append('<option value="%s"%s>%s</option>'
                           % (interface,
                              interface == selected and ' selected' or '',
                              interface)
                           )


        search_field = '<input type="text" name="%s" value=\"%s\">' % (
            search_name, search_string)
        select_field = '<select name="%s">%s</select>'  % (
            select_name, ''.join(options))

        HTML = search_field + select_field
        return HTML

class DisplayWidget(BaseWidget, DisplayWidget):
    pass
