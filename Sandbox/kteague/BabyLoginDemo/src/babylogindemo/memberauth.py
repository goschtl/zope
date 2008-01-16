import grok

import base64
import urllib

from zope.interface import implements, alsoProvides
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal

class Nobody(object):
    # we could allow the Zope to return the zope.anybody principal
    # but this way is more explicit for demonstration purposes
    implements(IUnauthenticatedPrincipal)
    id = 'babylogindemo.ac'
    title = 'The Anonymous Coward'
    description = 'You are not logged in, eh'


class MemberAuthentication(grok.Model):
    "Authenticates against our own Members container"
    implements(IAuthentication)
    
    def authenticate(self, request):
        members = grok.getSite()['members']
        login = request.get('login', None)
        password = request.get('password', None)
        cookie = request.get('babylogindemo.auth', None)
        
        # if login and password are submitted with the request,
        # save them in a cookie, otherwise get the cookie and
        # extract the login and password from them
        if login and password:
            val = base64.encodestring('%s:%s' % (login, password))
            request.response.setCookie('babylogindemo.auth',
                                       urllib.quote(val),
                                       path='/')
        elif cookie:
            val = base64.decodestring(urllib.unquote(cookie))
            login, password = val.split(':')
        
        # XXX check the password, eh!
        try:
            return members[login]
        except KeyError:
            return None
    
    def unauthenticatedPrincipal(self):
        return Nobody()
    
    def unauthorized(self, id, request):
        return None
    
    def getPrincipal(self, id):
        members = grok.getSite()['members']
        try:
            return members[id]
        except KeyError:
            return None
