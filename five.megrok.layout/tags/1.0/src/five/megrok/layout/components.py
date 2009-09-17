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
from grokcore.formlib.components import default_form_template
from five import grok
from zope import component, interface

from Products.Five.browser.decode import processInputs, setPageEncoding

import Acquisition


class Layout(megrok.layout.Layout, Acquisition.Explicit):

    grok.baseclass()

    def __init__(self, *args):
        super(Layout, self).__init__(*args)
        if not (self.static is None):
            # static should be wrapper correctly with acquisition,
            # otherwise you will not be able to compute URL for
            # resources.
            self.static = self.static.__of__(self)

    # We let getPhysicalPath to be acquired. This make static URL's
    # work, and prevent us to inherit from Acquisition.Implicit
    getPhysicalPath = Acquisition.Acquired


class Page(megrok.layout.Page, Acquisition.Explicit):

    grok.baseclass()

    def __init__(self, *args):
        super(Page, self).__init__(*args)
        if not (self.static is None):
            # static should be wrapper correctly with acquisition,
            # otherwise you will not be able to compute URL for
            # resources.
            self.static = self.static.__of__(self)

    # We let getPhysicalPath to be acquired. This make static URL's
    # work, and prevent us to inherit from Acquisition.Implicit
    getPhysicalPath = Acquisition.Acquired


class Form(megrok.layout.Form, Acquisition.Explicit):

    grok.baseclass()

    def __init__(self, *args):
        super(Form, self).__init__(*args)
        self.__name__ = self.__view_name__
        # super seems not to work correctly since this is needed again.
        self.static = component.queryAdapter(
            self.request, interface.Interface,
            name = self.module_info.package_dotted_name)
        if not (self.static is None):
            self.static = self.static.__of__(self)

    def update_form(self):
        processInputs(self.request)
        setPageEncoding(self.request)
        super(Form, self).update_form()
