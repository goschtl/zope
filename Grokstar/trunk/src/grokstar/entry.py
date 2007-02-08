from datetime import datetime
from docutils.core import publish_parts

from zope import schema, interface
from zope.annotation.interfaces import IAttributeAnnotatable

from hurry.workflow.interfaces import IWorkflowInfo

import grok

from grokstar.blog import Blog
from grokstar import interfaces

class Entry(grok.Model):
    interface.implements(interfaces.IEntry, IAttributeAnnotatable)

    def __init__(self, title, summary, rightsinfo):
        self.title = title
        self.updated = datetime.now()
        self.published = None
        self.summary = summary
        self.rightsinfo = rightsinfo
        
class RestructuredTextEntry(Entry):
    interface.implements(interfaces.IRestructuredTextEntry)

    def __init__(self, title, summary, rightsinfo, content):
        super(RestructuredTextEntry, self).__init__(title, summary, rightsinfo)
        self.content = content

grok.context(RestructuredTextEntry)


class Index(grok.View):
    pass


class Item(grok.View):
    pass


class Add(grok.AddForm):
    grok.context(Blog)

    form_fields = grok.Fields(
        id=schema.TextLine(title=u"id"))
    form_fields += grok.AutoFields(RestructuredTextEntry).omit(
        'published', 'updated')

    @grok.action('Add entry')
    def add(self, id, **data):
        new_entry = RestructuredTextEntry(**data)
        self.context['entries'][id] = new_entry
        IWorkflowInfo(new_entry).fireTransition('create')
        self.redirect(self.url(self.context))


class Edit(grok.EditForm):
    form_fields = grok.AutoFields(RestructuredTextEntry).omit(
        'published', 'updated')

    @grok.action('Save changes')
    def edit(self, **data):
        self.applyChanges(**data)
        self.redirect(self.url(self.context))

    @grok.action('Publish')
    def publish(self, **data):
        self.applyChanges(**data)
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
