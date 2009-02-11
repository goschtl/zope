

from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication

class Switch(object):
    """WSGI application that switches to a pipeline based on the request type.

    Requires 'zope.request' in the environment.
    """
    implements(IWSGIApplication)

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        app = IWSGIApplication(request, name='pipeline')
        return app(environ, start_response)

    def __repr__(self):
        return '%s()' % self.__class__.__name__
