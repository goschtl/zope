import grok
import megrok.five
from zope import schema
from todolist.todoitem import TodoItem

class TodoList(megrok.five.Application):
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
        name = str(name) # Zope 2 doesn't like unicode names
        item = TodoItem(name, title)
        self.context._setObject(name, item)
        self.redirect(self.url(name))
        #self.redirect(getattr(self.context, name).absolute_url())

class DeleteItem(grok.View):

    def render(self, name):
        self.context.manage_delObjects([name])
        self.redirect(self.url(self.context))
