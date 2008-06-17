from datetime import datetime
from docutils.core import publish_parts

from zope import schema, interface
from zope.annotation.interfaces import IAttributeAnnotatable

from hurry.workflow.interfaces import IWorkflowInfo

import grok

from grokstar.blog import Blog, Index, Edit, Main, Right, AddEntry
from grokstar import interfaces
import grokstar.form

from zope.component import getUtility, getMultiAdapter

class Entry(grok.Container):
    interface.implements(interfaces.IEntry, IAttributeAnnotatable)

    def __init__(self, title, summary, categories=[]):
        grok.Container.__init__(self)
        self.title = title
        self.updated = self.published = datetime.now()
        self.summary = summary
        self.categories = categories

class RestructuredTextEntry(Entry):
    interface.implements(interfaces.IRestructuredTextEntry)

    def __init__(self, title='', summary='', content='', categories=[]):
        Entry.__init__(self, title, summary, categories)
        self.content = content

class Comment(grok.Model):
    interface.implements(interfaces.IComment, IAttributeAnnotatable)
    comment = u""
    date = datetime.now() 
    author = u""
    
    def __init__(self, comment, author):
        self.comment = comment
        self.author = author
        self.date = datetime.now()

grok.context(RestructuredTextEntry)

class EntryIndex(grok.Viewlet):
    grok.viewletmanager(Main)
    grok.view(Index)
    
    def update(self):
        self.comments=sorted(self.context.values(), key=lambda c:c.date)
    
class Item(grok.View):
    pass

class AddComment(grok.Viewlet):
    grok.context(Entry)
    grok.viewletmanager(Main)
    grok.view(Index)
    grok.order(8)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='addcommentform')
        self.form.update_form()

    def render(self):
        return self.form.renderedPreview + self.form.render()

class AddCommentForm(grokstar.form.GrokstarAddForm):
    form_fields = grok.AutoFields(Comment).omit('date')
    renderedPreview = ''    

    @grok.action('Preview')
    def preview(self, comment='', **data):
        self.renderedPreview = '<h2>Preview</h2><div class="comment">' + renderRest(comment) + '</div>'
        self.form_reset = False
    
    @grok.action('Add comment')
    def add(self, **data):
        new_comment = Comment(**data)
        cid = 1
        while str(cid) in self.context:
            cid += 1 #Not very clever, but fine for < 10000 comments!
        self.context[str(cid)] = new_comment
        self.redirect(self.url(self.context))


class AddEntryViewlet(grok.Viewlet):
    grok.viewletmanager(Main)
    grok.view(AddEntry)
    grok.context(Blog)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='addentryform')
        self.form.update_form()

    def render(self):
        return self.form.renderedPreview + self.form.render()

class AddEntryForm(grokstar.form.GrokstarAddForm):
    grok.context(Blog)
    
    form_fields = grok.Fields(
        id=schema.TextLine(title=u"id"))
    form_fields += grok.AutoFields(RestructuredTextEntry).omit(
        'published', 'updated')
    renderedPreview = ''

    @grok.action('Preview')
    def preview(self, content='', **data):
        self.renderedPreview = '<h2>Preview</h2><div class="comment">' + renderRest(content) + '</div>'
        self.form_reset = False

    @grok.action('Add draft entry')
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

class EntryEdit(grok.Viewlet):
    grok.context(Entry)
    grok.viewletmanager(Main)
    grok.view(Edit)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='entryeditform')
        self.form.update_form()

    def render(self):
        return self.form.renderedPreview + self.form.render()

class EntryEditForm(grok.EditForm):
    form_fields = grok.AutoFields(RestructuredTextEntry).omit(
        'published', 'updated')
    renderedPreview = ''

    @grok.action('Save changes')
    def edit(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context))

    @grok.action('Preview')
    def preview(self, content, **data):
        self.renderedPreview = renderRest(content)
        self.form_reset = False

    @grok.action('Publish')
    def publish(self, **data):
        self.applyData(self.context, **data)
        IWorkflowInfo(self.context).fireTransitionToward(interfaces.PUBLISHED)
        self.redirect(self.url(self.context))

    @grok.action('Retract')
    def retract(self, **data):
        self.applyData(self.context, **data)
        IWorkflowInfo(self.context).fireTransitionToward(interfaces.CREATED)
        self.redirect(self.url(self.context))

class RenderedComment(grok.View):
    grok.context(Comment)
    def render(self):
        return renderRest(self.context.comment)

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
