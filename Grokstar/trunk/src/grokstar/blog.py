import random
from datetime import datetime, timedelta
from itertools import islice

from zope import schema, interface
from zope.interface import Interface
from zope.traversing.api import getParents
from hurry.query.query import Query
from hurry import query
from hurry.workflow.interfaces import IWorkflowState

import grok
from grok import index
from grokstar.interfaces import IRestructuredTextEntry, IBlog
from grokstar.interfaces import PUBLISHED, CREATED
from grokstar.base import ViewBase

class Blog(grok.Container, grok.Application):
    interface.implements(IBlog)

    def __init__(self):
        super(Blog, self).__init__()
        self.title = ''
        self.tagline = ''
        self['entries'] = Entries()

class EntryIndexes(grok.Indexes):
    grok.site(Blog)
    grok.context(IRestructuredTextEntry)
    grok.name('entry_catalog')

    title = index.Text()
    content = index.Text()
    published = index.Field()

class WorkflowIndexes(grok.Indexes):
    grok.site(Blog)
    grok.context(IWorkflowState)
    grok.name('entry_catalog')

    workflow_state = index.Field(attribute='getState')
    workflow_id = index.Field(attribute='getId')


class Drafts(grok.Model):
      pass

class DraftsIndex(ViewBase):
    grok.context(Drafts)
    grok.name('index')
    
    def entries(self): 
        return allEntries(10)

class Entries(grok.Container):
    pass

class BlogIndex(ViewBase):
    grok.context(Blog)
    grok.name('index')

    def entries(self):
        return lastEntries(10)

class BlogMacros(ViewBase):
    grok.context(Interface)

class BlogEdit(grok.EditForm, ViewBase):
    grok.context(Blog)
    grok.name('edit')

    @grok.action('Save changes')
    def edit(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context))

class BlogAbout(ViewBase):
    grok.context(Blog)
    grok.name('about')

class Search(ViewBase):
    grok.context(Blog)

    def update(self, q=None):
        if q is None:
            return self.redirect(self.application_url())

        q = q.strip()
        if not q:
            self.results = lastEntries(10)
            return

        entries = Query().searchResults(
            (query.Eq(('entry_catalog', 'workflow_state'), PUBLISHED) &
             (query.Text(('entry_catalog', 'title'), q) |
              query.Text(('entry_catalog', 'content'), q))))
        self.results = list(islice(entries, 10))

class EntriesIndex(ViewBase):
    grok.context(Entries)
    grok.name('index')

    def entries(self):
        return lastEntries(10)

def lastEntries(amount):
    entries = Query().searchResults(
        query.Eq(('entry_catalog', 'workflow_state'),
                  PUBLISHED))
    return sorted(
        entries, key=lambda entry: entry.published, reverse=True
        )[:amount]

def allEntries(amount):
    entries = Query().searchResults(
        query.In(('entry_catalog', 'workflow_state'),
                  (CREATED,)))

    return sorted(
        entries, key=lambda entry: entry.updated, reverse=True
        )[:amount]
