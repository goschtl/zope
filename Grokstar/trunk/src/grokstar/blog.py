import random
from datetime import datetime, timedelta
from itertools import islice

from zope import schema, interface
from zope.interface import Interface
from zope.traversing.api import getParents
from zope.component import getUtility, getMultiAdapter
from hurry.query.query import Query
from hurry import query
from hurry.query.set import AllOf
from hurry.workflow.interfaces import IWorkflowState

import grok
from grok import index
from grokstar.interfaces import IEntry, IBlog, PUBLISHED, CREATED
from zope.app.catalog.interfaces import ICatalog
grok.context(Interface)


class EditArticles(grok.Permission):
    grok.name('grokstar.Edit') # Single editing permission

class Blog(grok.Container, grok.Application):
    interface.implements(IBlog)
    title = 'Grokstar'
    tagline = 'A blogging app written with Grok'
    footer = ''
    email = ''

    def __init__(self):
        super(Blog, self).__init__()
        self['entries'] = Entries()


@grok.subscribe(Blog, grok.IObjectAddedEvent)
def registerAsUtility(app, event):
    app.getSiteManager().registerUtility(app, grok.interfaces.IApplication)

class Index(grok.View):    
    grok.template('layout')

class Edit(grok.View):
    grok.require('grokstar.Edit')
    grok.template('layout')

class AddEntry(grok.View):
    grok.require('grokstar.Edit')
    grok.template('layout')


class Head(grok.ViewletManager):
    grok.name('head')
    
class Main(grok.ViewletManager):
    grok.name('main')

class Right(grok.ViewletManager):
    grok.name('right')

class Top(grok.ViewletManager):
    grok.name('top')

class HtmlHead(grok.Viewlet):
    grok.viewletmanager(Head)
    grok.order(0)

    def getAppTitle(self):
        """Get the title of our blog.
        """
        return grok.getSite().title
    
class CssHead(grok.Viewlet):
    grok.viewletmanager(Head)
    grok.order(1)

class TitleHeader(grok.Viewlet):
    grok.viewletmanager(Top)


class EntryIndexes(grok.Indexes):
    grok.site(Blog)
    grok.context(IEntry)
    grok.name('entry_catalog')

    title = index.Text()
    content = index.Text()
    published = index.Field()
    categories = index.Set()

class WorkflowIndexes(grok.Indexes):
    grok.site(Blog)
    grok.context(IWorkflowState)
    grok.name('entry_catalog')

    workflow_state = index.Field(attribute='getState')
    workflow_id = index.Field(attribute='getId')


class Drafts(grok.Model):
      pass


class Search(grok.Viewlet):
    grok.viewletmanager(Right)
    grok.order(-1)

    def update(self):
        if 'q' not in self.request.form:
            return

        q = self.request.form['q'].strip()
        if not q:
            self.results = lastEntries(10)
            return

        entries = Query().searchResults(
            (query.Eq(('entry_catalog', 'workflow_state'), PUBLISHED) &
             (query.Text(('entry_catalog', 'title'), q) |
              AllOf(('entry_catalog', 'categories'), [q]) |
              query.Text(('entry_catalog', 'content'), q))))
        self.results = list(islice(entries, 10))


class DraftsIndex(grok.Viewlet):
    grok.context(Drafts)
    grok.require('grokstar.Edit')
    grok.viewletmanager(Main)
    
    def entries(self): 
        return allEntries(10)

class Entries(grok.Container):
    pass

class BlogIndex(grok.Viewlet):
    grok.context(Blog)
    grok.viewletmanager(Main)
    grok.view(Index)

    def entries(self):
        return lastEntries(10)

class BlogEdit(grok.Viewlet):
    grok.context(Blog)
    grok.viewletmanager(Main)
    grok.view(Edit)
    
    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='blogeditform')
        self.form.update_form()

    def render(self):
        return self.form.render()

class BlogEditForm(grok.EditForm):
    grok.context(Blog)
    
    @grok.action('Save changes')
    def edit(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context))

class EntriesIndex(grok.Viewlet):
    grok.context(Entries)
    grok.viewletmanager(Main)

    @property
    def entries(self):
        """Return all published entries.
        """
        return lastEntries(-1)

class RecentEntries(grok.Viewlet):
    grok.viewletmanager(Right)
    
    def entries(self):
        return lastEntries(40)

def lastEntries(amount):
    entries = Query().searchResults(
        query.Eq(('entry_catalog', 'workflow_state'),
                  PUBLISHED))
    result = sorted(
        entries, key=lambda entry: entry.published, reverse=True
        )
    if amount == -1:
        # Return all published entries
        return result
    return result[:amount]

def allEntries(amount):
    entries = Query().searchResults(
        query.In(('entry_catalog', 'workflow_state'),
                  (CREATED,)))

    return sorted(
        entries, key=lambda entry: entry.updated, reverse=True
        )[:amount]

class Categories(grok.Viewlet):
    grok.viewletmanager(Right)
    c = None

    def categories(self):
        cat = getUtility(ICatalog, 'entry_catalog')
        categories = cat['categories']
        return categories.values()

    def update(self):
        if 'c' not in self.request.form:
            return

        self.c = self.request.form['c']

        self.entries = Query().searchResults(
                (query.Eq(('entry_catalog', 'workflow_state'), PUBLISHED) &
                  AllOf(('entry_catalog', 'categories'), [self.c])))

class Breadcrumbs(grok.Viewlet):
    grok.viewletmanager(Top)
    grok.context(Interface)
    grok.order(10)
    
    def parents(self):
        parent_list = getParents(self.context)
        parent_list.reverse()
        return parent_list[1:]
    
    def getName(self, obj):
        """Get a name for an object.
        """
        if IBlog.providedBy(obj):
            return obj.title
        elif isinstance(obj, Entries):
            return 'All Entries'
        return getattr(obj, '__name__', '')
