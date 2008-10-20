##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Test pagelet for functional testing.

$Id$
"""

from z3c.pagelet.browser import BrowserPagelet
import zope.interface
import zope.schema
import z3c.form 
import z3c.formui.form 
from z3c.formjs import ajax, jsaction
import z3c.form.form

from z3c.pagelet.browser import BrowserPagelet
from zope.viewlet.viewlet import CSSViewlet, JavaScriptViewlet

class DemoPagelet(BrowserPagelet):
    def update(self):
        pass
    def render(self):
        return 'PAGELET CONTENT'

DemoCSSViewlet = CSSViewlet('demo.css')
DemoJSViewlet = JavaScriptViewlet('demo.js')

class IDemoForm(zope.interface.Interface):
    field1 = zope.schema.TextLine(title=u'Field 1')

class DemoForm(z3c.formui.form.EditForm):
    label="Demo Form"
    fields = z3c.form.field.Fields(IDemoForm)
    ignoreContext = True

    def getContent(self):
        return {
            'field1': None
        }
        
class DemoFormJS(ajax.AJAXRequestHandler, DemoForm):
    z3c.form.form.extends(DemoForm)

    @jsaction.buttonAndHandler(u'Alert')
    def setupAlert(self, event, selecter):
        return """
            alert('CANCEL');
            return(false);
        """


