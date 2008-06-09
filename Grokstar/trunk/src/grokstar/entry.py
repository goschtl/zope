from datetime import datetime
from docutils.core import publish_parts

from zope import schema, interface
from zope.annotation.interfaces import IAttributeAnnotatable

from hurry.workflow.interfaces import IWorkflowInfo

import grok

from grokstar.blog import Blog
from grokstar import interfaces
from form import GrokstarAddForm, GrokstarEditForm

class Entry(grok.Model):
    interface.implements(interfaces.IEntry, IAttributeAnnotatable)

    def __init__(self, title, summary, rightsinfo, categories=None):
        self.title = title
        self.updated = datetime.now()
        self.published = None
        self.summary = summary
        self.rightsinfo = rightsinfo
        if categories is None:
            self.categories = []
        else:
            self.categories = categories

class RestructuredTextEntry(Entry):
    interface.implements(interfaces.IRestructuredTextEntry)

    def __init__(self, title, summary, rightsinfo, content, categories=None):
        super(RestructuredTextEntry, self).__init__(title, summary, rightsinfo, categories)
        self.content = content

grok.context(RestructuredTextEntry)


class Index(grok.View):
    pass


class Item(grok.View):
    def format_published(self, published_date):
        return published_date.strftime('%Y-%m-%d')


class Add(GrokstarAddForm):
    grok.context(Blog)
    title = u'Add Entry'
    # add the url that the user wants
    form_fields = grok.Fields(
        id=schema.TextLine(title=u"Post slug"))
    # don't show them these timestamps
    form_fields += grok.AutoFields(RestructuredTextEntry).omit(
        'published', 'updated')

    @grok.action('Add entry')
    def add(self, id, **data):
        new_entry = RestructuredTextEntry(**data)
        self.context['entries'][id] = new_entry
        IWorkflowInfo(new_entry).fireTransition('create')
        self.redirect(self.url(self.context))

    @grok.action('Add published entry')
    def add_published(self, id, **data):
        new_entry = RestructuredTextEntry(**data)
        self.context['entries'][id] = new_entry
        IWorkflowInfo(new_entry).fireTransition('create')
        IWorkflowInfo(new_entry).fireTransitionToward(interfaces.PUBLISHED)        
        self.redirect(self.url(self.context))


class Edit(GrokstarEditForm):
    grok.context(RestructuredTextEntry)
    title = u'Edit Entry'
    form_fields = grok.AutoFields(RestructuredTextEntry).omit(
        'published', 'updated')

    @grok.action('Save changes')
    def edit(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context))

    @grok.action('Publish')
    def publish(self, **data):
        self.applyData(self.context, **data)
        IWorkflowInfo(self.context).fireTransitionToward(interfaces.PUBLISHED)
        self.redirect(self.url(self.context))


class RenderedContent(grok.View):
    def render(self):
        return renderRest(self.context.content)


rest_settings = {
    # Disable inclusion of external files, which is a security risk.
    'file_insertion_enabled': False,
    # Disable the promotion of a lone top-level section title to document title
    # (and disable the promotion of a subsequent section title to document
    # subtitle).
    'doctitle_xform': False
    }

def renderRest(source):
    return publish_parts(
        source, writer_name='html', settings_overrides=rest_settings
        )['html_body']
