import grok
import megrok.five
from zope import schema
from todolist.todoitem import TodoItem

class TodoList(megrok.five.Container, grok.Application):
    pass

class Index(grok.View):
    pass

class AddTodoItem(grok.AddForm):

    form_fields = grok.Fields(
        title = schema.TextLine(title=u'Title')
        )

    @grok.action('Add')
    def add(self, title):
        name = title.lower().replace(' ', '-')
        item = TodoItem(name, title)
        self.context[name] = item
        self.redirect(self.url(name))

class DeleteItem(grok.View):

    def render(self, name):
        del self.context[name]
        self.redirect(self.url(self.context))
