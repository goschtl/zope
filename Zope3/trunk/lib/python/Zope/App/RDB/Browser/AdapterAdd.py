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
"""Zope database adapter adding view

$Id: AdapterAdd.py,v 1.2 2002/12/12 11:32:34 mgedmin Exp $
"""
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.ComponentArchitecture import getFactory

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Container.IAdding import IAdding


class AdapterAdd(BrowserView):
    """A base class for Zope database adapter adding views.

    Subclasses need to override _adapter_factory_id.
    """

    __used_for__ = IAdding

    # This needs to be overridden by the actual implementation
    _adapter_factory_id = None

    add = ViewPageTemplateFile('add.pt')

    def action(self, dsn):
        factory = getFactory(self, self._adapter_factory_id)
        adapter = factory(dsn)
        self.context.add(adapter)
        self.request.response.redirect(self.context.nextURL())
