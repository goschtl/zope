#############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

import megrok.layout
from five import grok
from zope import component, interface

from Products.Five.browser.decode import processInputs, setPageEncoding


class Layout(megrok.layout.Layout):

    grok.baseclass()

    def __init__(self, *args):
        super(Layout, self).__init__(*args)
        if not (self.static is None):
            # Set parent to get acquisition chain
            self.static.__parent__ = self.context


class Page(megrok.layout.Page):

    grok.baseclass()

    def __init__(self, *args):
        super(Page, self).__init__(*args)
        if not (self.static is None):
            # Set parent to get acquisition chain
            self.static.__parent__ = self.context


class Form(megrok.layout.Form):

    grok.baseclass()

    def __init__(self, *args):
        super(Form, self).__init__(*args)
        self.__name__ = self.__view_name__
        # super seems not to work correctly since this is needed again.
        self.static = component.queryAdapter(
            self.request, interface.Interface,
            name = self.module_info.package_dotted_name)
        if not (self.static is None):
            self.static.__parent__ = self.context

    def update_form(self):
        processInputs(self.request)
        setPageEncoding(self.request)
        super(Form, self).update_form()
