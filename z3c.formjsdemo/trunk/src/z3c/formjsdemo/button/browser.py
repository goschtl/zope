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
"""Browser code for JS button demo.

$Id: layer.py 75942 2007-05-24 14:53:46Z srichter $
"""
__docformat__="restructuredtext"
import os.path
import zope.interface
from zope.viewlet.viewlet import CSSViewlet
from z3c.form import form, button, field
from z3c.form.interfaces import IWidgets
from z3c.formui import layout
from z3c.formjs import jsaction, jsevent

ButtonCSSViewlet = CSSViewlet('button.css')

class IButtons(zope.interface.Interface):
    show = jsaction.JSButton(title=u'Show JavaScript')
    hide = jsaction.JSButton(title=u'Hide JavaScript')

class IFields(zope.interface.Interface):
    file = zope.schema.Choice(
        title=u"File",
        description=u"The file to show.",
        required=True,
        default=u"None",
        values=(u"None", u"browser.py", u"button.pt", u"configure.zcml")
        )

class ButtonForm(layout.FormLayoutSupport, form.Form):
    buttons = button.Buttons(IButtons)
    fields = field.Fields(IFields)

    @jsaction.handler(buttons['show'])
    def apply(self, event, selector):
        return '$("#javascript").slideDown()'

    @jsaction.handler(buttons['hide'])
    def apply(self, event, selector):
        return '$("#javascript").slideUp()'

    @jsaction.handler(fields['file'], event=jsevent.CHANGE)
    def handleFileChange(self, event, selector):
        id = selector.widget.id
        return '''
            $(".code").hide();
            $("#"+$("#%s").val().replace(".","-")).show();''' % id

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()

    def getFile(self, filename):
        here = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(here, filename), 'r')
        data = f.read()
        f.close()
        return data
