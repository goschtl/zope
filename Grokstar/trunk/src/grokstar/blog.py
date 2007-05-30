import random
from datetime import datetime, timedelta

from zope import schema

from hurry.query.query import Query
from hurry import query
from hurry.workflow.interfaces import IWorkflowState

import grok
from grok import index

from grokstar.interfaces import IEntry, PUBLISHED

class Blog(grok.Container, grok.Application):

    class fields:
        title = schema.TextLine(title=u'Title', default=u'')
        tagline = schema.TextLine(title=u'Tagline', default=u'')

    def __init__(self):
        super(Blog, self).__init__()
        self['entries'] = Entries()

class BlogIndexes(grok.Indexes):
    grok.site(Blog)
    grok.context(IEntry)
    grok.name('entry_catalog')

    published = Field(attribute='published')

class BlogIndexes(grok.Indexes):
    grok.site(Blog)
    grok.context(IWorkflowState)
    grok.name('entry_catalog')

    workflow_state = Field(attribute='getState')
    workflow_id = Field(attribute='getId')

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
        self.applyData(self.context, **data)
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
