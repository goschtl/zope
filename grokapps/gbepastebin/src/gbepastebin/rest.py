import sys
import simplejson
from pygments import lexers
import grok

from gbepastebin.app import Application
from gbepastebin.paste import Paste as PasteBase

"""
REST Application Namespace
==========================

Request     Method                          Returns                  Role
----------- ------- ----------------------- ------------------------ ---------            
/           GET     list all pastes         ['pasteid', ...]         Anonymous
/           POST    add new paste           'pasteid'                Anonymous
/<id>       GET     return paste (id)       Paste                    Anonymous
/<id>       DELETE  delete paste (id)       Boolean                  Manager
/languages  GET     list languages          [('alias', 'name'), ...] Anonymous

"""

class JSONLayer(grok.IRESTLayer):
   pass

class JSONProtocol(grok.RESTProtocol):
   grok.layer(JSONLayer)
   grok.name('json')

class BaseApplication(object):
    
    def list_pastes(self):
        pasteids=self.context.list_pasteids()
        site=grok.getSite()
        site_url=grok.url(self.request,site)
        return ['%s/%s' % (site_url, pasteid) for pasteid in pasteids]
    
    def add_paste(self):
        author_name=self.request.get('author_name')
        paste=self.request.get('paste')
        language=self.request.get('language')
        paste_obj=PasteBase(author_name, paste, language)
        return self.context.add_paste(paste_obj)
        
class JSONApplication(grok.REST, BaseApplication):
    grok.context(Application)
    grok.layer(JSONLayer)
    
    def GET(self):
        return simplejson.dumps(self.list_pastes())
    
    def POST(self):
        return simplejson.dumps(self.add_paste())

class Utils(grok.Model):
    
    def list_languages(self):
        all_lexers = list(lexers.get_all_lexers())
        lexer_info = []
        for name, aliases, filetypes, mimetypes_ in all_lexers:
                lexer_info.append((aliases[0], name))
        return lexer_info        

class JSONLanguages(grok.REST):
    grok.context(Utils)
    grok.layer(JSONLayer)
    
    def GET(self):
        return simplejson.dumps(self.context.list_languages())
        
class JSONPaste(grok.REST):
    grok.context(PasteBase)
    grok.layer(JSONLayer)

    def GET(self):
        return simplejson.dumps(self.context.to_dict())
    
    @grok.require('gbepastebin.manage')
    def DELETE(self):
        pasteid=self.context.pasteid
        site=grok.getSite()
        return simplejson.dumps(site.delete_paste(pasteid))
    
