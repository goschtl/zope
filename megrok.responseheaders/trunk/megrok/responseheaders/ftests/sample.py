import grok

from megrok.responseheaders import http_cache_control, http_content_type

class Sample(grok.Application, grok.Container):
    pass

class Index(grok.View):
    def render(self): 
        return "Index view"
    
class DoCache(grok.View):
    grok.name('do')
    
    http_cache_control(days=10)
    
    def render(self):
        return "Cached"
    
    
class DoCache2(grok.View):
    grok.name('do2')
    
    http_cache_control(seconds=1, minutes=1, hours=1, days=1, years=1)
    
    def render(self):
        return "Cached"    
    
class DontCache(grok.View):
    grok.name('dont')

    http_cache_control(private=True)
    
    def render(self):
        return "Not cached"
    
class Template1(grok.View):
    grok.template('template1')
    
class Template2(grok.View):
    grok.template('template2')
    

    
# This is a rather advanced case since we're setting a non-text
# content type on something where we don't manually control the
# rendering method. 
# Normally, if you do something like rendering the bulk of a CSV
# file for example as the output of the view you'll write your 
# own render() method and make sure you render it correctly.
# Zope will, on HTML content try to be clever and check the 
# content type and if you try to mess with that the publisher will
# raise an error basically saying that if you want to use a 
# special content type you're on your own.

from zope.publisher.interfaces.http import IResult, IHTTPRequest
@grok.adapter(unicode, IHTTPRequest)
@grok.implementer(IResult)
def myresultadapter(string, request):
    if request.response.getHeader('content-type',''
      ).startswith('application/xhtml+xml'):
        return string.encode('utf-8')
    
class Template3(grok.View):
    
    http_content_type('application/xhtml+xml')
        
    grok.template('template2')
    
    
