import grok
import megrok.five
from zope import schema

class TodoItem(megrok.five.Model):

    def __init__(self, id, title):
        self.id = id
        self.title = title

class Index(grok.View):
    pass

class Edit(grok.EditForm):

    form_fields = grok.Fields(
        title = schema.TextLine(title=u'Title')
        )

    @grok.action('Save')
    def save(self, title):
        self.applyChanges(title=title)
        self.redirect(self.url(self.context))
