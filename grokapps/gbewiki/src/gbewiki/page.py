import grok
from zope.component import getAdapter

from gbewiki.interface import Master
from gbewiki.utils import ITransform

default_page_name = 'MainPage'

class Page(grok.Model):
    """Page object, holds the Wikipage data
    """
    
    def __init__(self, name=''):
        super(Page, self).__init__()
        self.name=name
        self.content = '<h1>%s</h1>' % name
        self.editor=None

class Index(Master):

    def wikified_content(self):
        self.content = self.context.content
        self.default_page_name = default_page_name
        self.page_name=self.context.__name__
        self.wordlist=self.list_of_pages()

        transforms = [
          'wiki.AutoLink',
          'wiki.ListOfPages',
          'wiki.WikiWords',
        ]
       
        for transform in transforms:
            self.content = getAdapter(self, ITransform, transform).run()
        return self.content
    
    def list_of_pages(self):
        parent=self.context.__parent__
        return parent.keys()
    
    def update(self):
        if not(self.isWikiName(self.context.__name__)):
            self.flash('&raquo;%s&laquo; is not a valid page name. Use '
                       ' something like &raquo;WikiName&laquo; instead' \
                       % self.context.__name__)
            self.redirect(self.application_url())
            return
        if not(self.exists(self.context.__name__)):
               self.flash('Page &raquo;%s&laquo; created. You need to edit and \
               save the page to '
                          'store it to the database' % self.context.__name__)
    
class Edit(Master):
    grok.require('wiki.EditPage')
   
    def update(self):
        if not self.exists(self.context.__name__):
            self.action='%s/@@add' % self.application_url()
        else:
            self.action='%s/%s/@@save' % (self.application_url(),self.context.name)
    
class Save(grok.View):
    grok.require('wiki.EditPage')
    
    def render(self):
       self.context.content=self.request['content']
       self.context.editor=self.request.principal.title
       grok.notify(grok.ObjectModifiedEvent(self.context))
       self.flash('Page is saved')
       self.redirect('%s/%s' % (self.application_url(),self.context.name))
