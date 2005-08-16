##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Catalog Views

$Id: catalog.py,v 1.3 2004/03/17 17:59:28 srichter Exp $
"""
from zope.app.container.browser.adding import Adding
from zope.app.catalog.interfaces.catalog import ICatalog

class CatalogEditView:
    "Provides a user interface for configuring a catalog"

    __used_for__ = ICatalog

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def subscribe(self, update=False):
        self.context.subscribeEvents(update)
        self.request.response.redirect(".")

    def unsubscribe(self):
        self.context.unsubscribeEvents()
        self.request.response.redirect(".")

    def clear(self):
        self.context.clearIndexes()
        self.request.response.redirect(".")

    def reindex(self):
        self.context.updateIndexes()
        self.request.response.redirect(".")


class IndexAdding(Adding):
    menu_id = 'catalog_index_menu'

