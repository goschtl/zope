import grok
from zope.index.text.interfaces import ISearchableText
from todolist.interfaces import ITodoItem

grok.define_permission('todolist.ViewTodoItem')

class TodoItem(grok.Model):
    grok.implements(ITodoItem)

    def __init__(self, title, priority):
        self.title = title
        self.priority = priority

class TodoItemSearchableText(grok.Adapter):
    grok.implements(ISearchableText)

    def getSearchableText(self):
        return self.context.title

class Index(grok.View):
    grok.require('todolist.ViewTodoItem')

class Edit(grok.EditForm):
    form_fields = grok.AutoFields(TodoItem)

    @grok.action('Save changes')
    def save(self, **data):
        self.applyChanges(**data)
        self.redirect(self.url(self.context))
