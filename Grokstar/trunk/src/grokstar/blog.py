import random
from datetime import datetime, timedelta

from zope import schema
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.catalog import Catalog
from zope.app.catalog.interfaces import ICatalog
from zope.app.catalog.field import FieldIndex

from hurry.query.query import Query
from hurry import query
from hurry.workflow.interfaces import IWorkflowState

import grok

from grokstar.interfaces import IEntry, PUBLISHED

def setup_catalog(catalog):
    catalog['published'] = FieldIndex('published', IEntry)
    catalog['workflow_state'] = FieldIndex('getState', IWorkflowState, True)
    catalog['workflow_id'] = FieldIndex('getId', IWorkflowState, True)
    
class Blog(grok.Container, grok.Site):

    grok.local_utility(IntIds, provides=IIntIds)
    grok.local_utility(Catalog, provides=ICatalog, name='entry_catalog',
                       setup=setup_catalog)
    
    class fields:
        title = schema.TextLine(title=u'Title', default=u'')
        tagline = schema.TextLine(title=u'Tagline', default=u'')

    def __init__(self):
        super(Blog, self).__init__()
        self['entries'] = Entries()

class Entries(grok.Container):
    pass

class BlogIndex(grok.View):
    grok.context(Blog)
    grok.name('index')

    def entries(self):
        return lastEntries(10)

class BlogEdit(grok.EditForm):
    grok.context(Blog)
    grok.name('edit')

    @grok.action('Save changes')
    def edit(self, **data):
        self.applyChanges(**data)
        self.redirect(self.url(self.context))

class EntriesIndex(grok.View):
    grok.context(Entries)
    grok.name('index')

    def render(self):
        return "Entries: %s" % ' '.join(self.context.keys())

def lastEntries(amount):
    entries = Query().searchResults(
        query.Eq(('entry_catalog', 'workflow_state'),
                  PUBLISHED))

    return sorted(
        entries, key=lambda entry: entry.published, reverse=True
        )[:amount]
