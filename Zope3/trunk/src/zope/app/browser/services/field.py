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

$Id: field.py,v 1.3 2003/01/09 17:28:40 stevea Exp $
"""
__metaclass__ = type

from zope.app.browser.form.widget import BrowserWidget
from zope.component import getServiceManager

class ComponentPathWidget(BrowserWidget):

    def _convert(self, value):
        return value or None

    def __call__(self):
        selected = self._showData()
        service_manager = getServiceManager(self.context.context)
        info = service_manager.queryComponent(self.context.type)
        result = []

        result.append('<select name="%s">' % self.name)
        result.append('<option></option>')

        for item in info:
            item = item['path']
            if item == selected:
                result.append('<option selected>%s</option>' % item)
            else:
                result.append('<option>%s</option>' % item)

        result.append('</select>')

        return "\n".join(result)
