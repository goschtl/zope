from persistence import Persistent
from zope.interface import implements
from zope.component import getAdapter

from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent, ObjectModifiedEvent

from zope.app.index.field.index import FieldIndex
from zope.app.index.text.index import TextIndex

from zope.app.interfaces.container import IAdding

from zope.app.browser.container.adding import Adding

from zope.app.catalog.catalog import Catalog

import time

from zope.app.interfaces.catalog.catalog import ICatalog, ICatalogView

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

