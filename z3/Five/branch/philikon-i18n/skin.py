##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Mimick the Zope 3 skinning system in Five.

$Id$
"""
from zope.interface.common.mapping import IItemMapping
from zope.interface import implements
from zope.component import getView
from Products.Five.browser import BrowserView

# this is a verbatim copy of zope.app.basicskin except that it doesn't
# derive from ``object``
class Macros:
    implements(IItemMapping)

    macro_pages = ()
    aliases = {
        'view': 'page',
        'dialog': 'page',
        'addingdialog': 'page'
        }

    def __getitem__(self, key):
        key = self.aliases.get(key, key)
        context = self.context
        request = self.request
        for name in self.macro_pages:
            page = getView(context, name, request)
            try:
                v = page[key]
            except KeyError:
                pass
            else:
                return v
        raise KeyError, key


class StandardMacros(BrowserView, Macros):
    macro_pages = ('five_template',
                   'widget_macros',
                   'form_macros',) 

# copy of zope.app.form.browser.macros.FormMacros
class FormMacros(StandardMacros):    
    macro_pages = ('widget_macros', 'addform_macros')
