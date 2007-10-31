##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Widget Switch Content

$Id$
"""
__docformat__="restructuredtext"
import zope.component
import zope.interface
from zope.session.interfaces import ISession
from zope.viewlet.viewlet import CSSViewlet, JavaScriptViewlet

from z3c.form import field, form
from z3c.form.interfaces import IWidgets, DISPLAY_MODE
from z3c.formjs import jsswitch
from z3c.formui import layout
from z3c.formjsdemo.widgetswitch import interfaces, content

WidgetSwitchJSViewlet = JavaScriptViewlet('jquery-switch.js')
WidgetSwitchCSSViewlet = CSSViewlet('widgetswitch.css')

class ContactForm(layout.FormLayoutSupport,
                  jsswitch.WidgetModeSwitcher,
                  form.EditForm):
    fields = field.Fields(interfaces.IContact)
    label = u'Contact Edit Form'

    def getContent(self):
        session = ISession(self.request)['z3c.formjsdemo.widgetswitch']
        obj = session.get('content')
        if obj is None:
            obj = session['content'] = content.Contact()
            # Initialize data.
            obj.name = u'Stephan Richter'
            obj.street = u'110 Main Street'
            obj.city = u'Maynard'
            obj.zip = u'01754'
            obj.phone = u'(555) 373-2134'
            obj.age = 27
        return obj
