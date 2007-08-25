import grok
import hurry.query.value

from zope import component
from zope.index.text.interfaces import ISearchableText
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.catalog.catalog import Catalog
from zope.app.catalog.interfaces import ICatalog
from zope.app.catalog.text import TextIndex
from zc.catalog.catalogindex import ValueIndex

from todolist.interfaces import ITodoItem
from todolist.todoitem import TodoItem
from todolist.priority import Priority

def setup_catalog(catalog):
    catalog['fulltext'] = TextIndex('getSearchableText', ISearchableText, True)
    catalog['created'] = ValueIndex('created', IZopeDublinCore, False)
    catalog['modified'] = ValueIndex('modified', IZopeDublinCore, False)
    catalog['priority'] = ValueIndex('priority', ITodoItem, False)

class SnowPlow(grok.Application, grok.Container):
    grok.local_utility(IntIds, provides=IIntIds) # necessary for catalog
    grok.local_utility(Catalog, provides=ICatalog, setup=setup_catalog)

    def traverse(self, name):
        if name == 'last':
            catalog = component.getUtility(ICatalog)
            last_modification_date = catalog['created'].maxValue()
            last = catalog.searchResults(created={'any_of':
                                                  (last_modification_date,)})
            return list(last)[0]
        if name == 'by-priority':
            return ByPriority()

grok.context(SnowPlow)

class ByPriority(grok.Model):

    def traverse(self, name):
        return Priority(name)

class Index(grok.View):
    pass

class AddTodoItem(grok.AddForm):
    form_fields = grok.AutoFields(ITodoItem)

    @grok.action('Add')
    def add(self, title, priority):
        id = title.lower().replace(' ', '-')
        self.context[id] = todoitem = TodoItem(title, priority)
        grok.notify(grok.ObjectCreatedEvent(todoitem))
        self.redirect(self.url(self.context))

class DeleteItem(grok.View):

    def update(self):
        name = self.request.form.get('name', None)
        if name is not None:
            del self.context[name]
            self.redirect(self.url(self.context))

class Search(grok.View):

    def update(self):
        query = self.request.form.get('query')
        self.search_results = []
        if query is not None:
            catalog = component.getUtility(ICatalog)
            self.search_results = catalog.searchResults(fulltext=query)

import megrok.kiss

class DeleteKSS(megrok.kiss.AjaxAction):

    def action(self):
        name = self.request.form.get('name', None)
        if name is not None:
            del self.context[name]
            self.core.deleteNode(self.core.getHtmlIdSelector('item-' + name))

class EditKSS(megrok.kiss.AjaxAction):

    def action(self):
        name = self.request.form.get('name', None)
        if name is not None:
            item = self.context[name]
            self.core.replaceInnerHTML(
                self.core.getHtmlIdSelector('title-' + name),
                '<input type="text" name="title" value="%s" />' % item.title
                )
            self.core.replaceInnerHTML(
                self.core.getHtmlIdSelector('edit-' + name),
                '<input type="submit" value="Save" class="edit-submit kukit-name-%s" />' % name
                )

class EditSaveKSS(megrok.kiss.AjaxAction):

    def action(self):
        name = self.request.form.get('name', None)
        if name is not None:
            item = self.context[name]
            title = self.request.form.get('title')
            item.title = title

            self.core.replaceInnerHTML(
                self.core.getHtmlIdSelector('title-' + name),
                '<a href="%s">%s</a>' % (self.url(item), title)
                )

            self.core.replaceInnerHTML(
                self.core.getHtmlIdSelector('edit-' + name),
                '<a href="%s">edit</a>' % self.url(item, 'edit')
                )
