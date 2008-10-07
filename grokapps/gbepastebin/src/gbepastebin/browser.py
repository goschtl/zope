import pygments
from pygments import lexers
from pygments import formatters
from pygments import util
from zope.interface import Interface
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.component import getUtility
import z3c.flashmessage.interfaces
import grok

from gbepastebin.app import Application
from gbepastebin.paste import Paste as PasteBase

formatter = formatters.HtmlFormatter(linenos=True, cssclass="source")
style_defs = formatter.get_style_defs()

COOKIE_AUTHOR='gbepastebin.last_author'
COOKIE_LANGUAGE='gbepastebin.last_language'

class PastebinMaster(grok.View):
    grok.context(Interface)

    def version(self):
        return grok.getSite().version

    def isManager(self):
        return self.request.principal.id == 'zope.manager'
    
    def messages(self):
        source = getUtility(
            z3c.flashmessage.interfaces.IMessageSource, name='session')
        for message in list(source.list('message')):
            message.prepare(source)
            yield message

class Index(PastebinMaster):
    grok.context(Application)
        
    def preferred_author(self):
        return self.request.cookies.get(COOKIE_AUTHOR,'')       
    
    def preferred_language(self):
        return self.request.cookies.get(COOKIE_LANGUAGE,'')       
  
    def lexers(self):
        all_lexers = list(lexers.get_all_lexers())
        lexer_info = []
        for name, aliases, filetypes, mimetypes_ in all_lexers:
                lexer_info.append((name.lower(),{'alias':aliases[0], 'name':name}))
        lexer_info.sort()
        return [value for key, value in lexer_info]
        

class Paste(grok.View):
    grok.context(Application)
    
    def update(self, author_name, language, paste):
        paste=paste.strip()
        if not(paste):
            self.flash('Blank paste. Please fill in some text.')
            return self.redirect(self.application_url())
        self.request.response.setCookie(COOKIE_AUTHOR, author_name)
        self.request.response.setCookie(COOKIE_LANGUAGE, language)
        paste=PasteBase(author_name, paste, language)
        self.pasteid=self.context.add_paste(paste)
        
    def render(self):
        self.flash('Created Paste #%s' % self.pasteid)
        return self.redirect(self.url(self.pasteid))

class Delete(grok.View):
    grok.context(PasteBase)
    grok.require('gbepastebin.manage')
    
    def update(self):
        site=grok.getSite()
        pasteid=self.context.pasteid
        success=site.delete_paste(pasteid)
        if success:
            self.flash('Deleted Paste #%s' % pasteid)
        else:
            self.flash('<b>Problem:</b> could not delete Paste #%s' % pasteid)
            
    def render(self):
        return self.redirect(self.url(grok.getSite()))
    
class Manage(PastebinMaster):
    grok.context(Application)
    grok.require('gbepastebin.manage')

    def isPlural(self, pastelist):
        if len(pastelist) > 1:
            return 's'
        return ''
    
    def update(self, delete=''):
        if self.request.form.get('form.submitted') and delete:
            success=self.context.delete_pastes(delete)
            if success:
                self.flash('Deleted Paste%s #%s' % (self.isPlural(delete) ,', '.join(delete)))
            else:
                self.flash('<b>Problem:</b> could not delete all Pastes requested')
            
class Entry(PastebinMaster):
    grok.context(PasteBase)
    grok.name('index')
        
    def application_url(self):
        site=grok.getSite()
        return self.url(site)
    
    def format(self):
        context = self.context
        language=''
        try:
            if context.language:
                l = lexers.get_lexer_by_name(context.language)
            else:
                l = lexers.guess_lexer(context.paste)
            language = l.name
        except util.ClassNotFound, err:
            # couldn't guess lexer
            l = lexers.TextLexer()

        formatted_paste = pygments.highlight(context.paste, l, formatter)
        return {'language': language,
                'formatted_paste': formatted_paste,
                'style_defs': style_defs}
