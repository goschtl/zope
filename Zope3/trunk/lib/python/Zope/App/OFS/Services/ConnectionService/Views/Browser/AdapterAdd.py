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
"""
$Id: AdapterAdd.py,v 1.1 2002/07/10 23:52:18 srichter Exp $
"""
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.ComponentArchitecture import getFactory

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Container.IAdding import IAdding


class AdapterAdd(BrowserView):
    """Provide a user interface for adding a contact"""
    
    __used_for__ = IAdding

    # This needs to be overridden by the actual implementation
    _adapter_factory_id = None

    add = ViewPageTemplateFile('add.pt')

    # action method
    def action(self, dsn):
        "Add a contact"
        factory = getFactory(self, self._adapter_factory_id)
        adapter = factory(dsn)
        self.context.add(adapter)
        self.request.response.redirect(self.context.nextURL())
