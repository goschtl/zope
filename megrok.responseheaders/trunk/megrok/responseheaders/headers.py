from time import time

import grok
from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.datetime import rfc1123_date

import martian
class http_content_type(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    
    def validate(self, value):
        # basic text test
        martian.validateText(self, value)
            
        # check the mime type
        mime_type = value.split(';')[0]
        if not mime_type.find('/') > 0:
            raise ValueError("Unexpected mimetype %r" % mime_type)
        
        # check the charset 
        if value.find('charset=') > -1:
            charset = value[value.find('charset=')+8:]
            try:
                unicode('s', charset)
            except LookupError:
                raise ValueError("Invalid charset value %r" % charset)
            

class http_cache_control(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    
    # an alternative to this `default=None` you can make a method
    # called get_default(...)
    default = None
    
    def factory(self, seconds=0, minutes=0, hours=0,
                days=0, years=0, private=False):
        """ return a dictionary containing all the valid parameters """
        parameters = locals()
        parameters.pop('self')
        
        return parameters
        

@grok.subscribe(grok.View, IBeforeTraverseEvent)
def handle(view, event):
    cache_control = http_cache_control.bind().get(view) # None or {'days'...}
    if cache_control:
        assert isinstance(cache_control, dict)
        for key, value in get_cache_headers(cache_control).items():
            event.request.response.setHeader(key, value)
            
    content_type = http_content_type.bind().get(view)
    charset = getattr(view, 'http_content_type_charset', 'utf-8')
    if content_type:
        if charset:
            event.request.response.setHeader('Content-Type', 
                                             '%s;charset=%s' % \
                                              (content_type, charset))
        else:
            event.request.response.setHeader('Content-Type', content_type)

        
def get_cache_headers(parameters):
    """ return a dict of suitable HTTP headers. The parameters can contain 
    the following keys:
        
        * seconds (int)
        * minutes (int)
        * hours (int)
        * days (int)
        * years (int)
        * private (bool)
        
    For whatever you pass, it will return both 'Cache-Control' and 'Expires'.
    """
    # First, convert whatever the parameters were into one variable 'hours'
    if parameters.get('private'):
        hours = -24
    else:
        hours = 0
        hours += parameters.get('seconds', 0) / 60.0 / 60
        hours += parameters.get('minutes', 0) / 60.0
        hours += parameters.get('hours', 0)
        hours += parameters.get('days', 0) * 24
        hours += parameters.get('years', 0) * 24 * 365
        
    # TODO: Verify that these are correct again.
    # TODO: Consider making the "public" optional
    if hours < 0:
        # All major sites lite google, yahoo and micrsoft use this
        return {'Cache-Control': 'private'}
        
        # Plone.org sets Expires to 1998 and Cache-Control to 
        # 'max-age=0, s-maxage=3600, must-revalidate'
    
        # This was the old way to do it. 
        #return {'Expires': rfc1123_date(time() + 3600 * int(hours)),
        #        'Cache-Control': 'private,max-age=0',
        #        'Pragma': 'no-cache'
        #        }
                
    else:
        seconds = int(round(3600 * hours))
        return {'Expires': rfc1123_date(time() + seconds),
                'Cache-Control': 
                     'public,max-age=%d' % seconds
                }
        
        
