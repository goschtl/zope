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
"""A widget for ComponentPath field.

$Id: field.py,v 1.17 2004/03/13 18:01:05 srichter Exp $
"""
from zope.app import zapi
from zope.app.browser.form.widget import BrowserWidget
from zope.app.registration.interfaces import IRegistrationManagerContainer

class ComponentPathWidget(BrowserWidget):

    def _convert(self, value):
        return value or None

    def __call__(self):
        selected = self._showData()
        field = self.context
        return renderPathSelect(field.context, field.type,
                                self.name, selected)


class ComponentPathDisplayWidget(ComponentPathWidget):

    def __call__(self):
        path = self._showData()
        path = canonicalPath(path)
        ob = zapi.traverse(self.context.context, path)
        url = str(zapi.getView(ob, 'absolute_url', self.request))
        url += "/@@SelectedManagementView.html"
        return '<a href="%s">%s</a>' % (url, path)


def queryComponent(ob, type):
    """Find the objects of the given type in the enclosing folder
    """
    o = ob
    while 1:
        if IRegistrationManagerContainer.providedBy(o):
            break
        if o is None:
            raise ValueError(o, "is not in a service manager container")
        o = o.__parent__

    result = []
    for name in o:
        value = o[name]
        if type.providedBy(value):
            result.append({'path': zapi.getPath(value),
                           'component': value,
                           })
    return result

def renderPathSelect(context, type, name, selected, empty_message=''):
    info = queryComponent(context, type)
    result = []

    result.append('<select name="%s">' % name)
    result.append('<option>%s</option>' % empty_message)

    for item in info:
        item = item['path']
        if item == selected:
            result.append('<option selected>%s</option>' % item)
        else:
            result.append('<option>%s</option>' % item)

    result.append('</select>')
    return ''.join(result)

