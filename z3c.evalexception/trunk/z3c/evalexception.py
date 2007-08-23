import zope.security.management
from paste.evalexception.middleware import EvalException

class ZopeEvalException(EvalException):
    """Wrapper around Paste's EvalException middleware that simply
    tells zope.publisher to let exceptions propagate to the middleware."""

    def __call__(self, environ, start_response):
        environ['wsgi.handleErrors'] = False
        return super(ZopeEvalException, self).__call__(environ, start_response)

def zope_eval_exception(app, global_conf):
    return ZopeEvalException(app)

def PostMortemDebug(application):
    """Middleware that catches exceptions coming from a
    zope.publisher-based application and invokes pdb's post-mortem
    debugging facility."""
    def middleware(environ, start_response):
        environ['wsgi.handleErrors'] = False
        try:
            for chunk in application(environ, start_response):
                yield chunk
        except:
            import sys, pdb
            print "%s:" % sys.exc_info()[0]
            print sys.exc_info()[1]
            zope.security.management.restoreInteraction()
            try:
                pdb.post_mortem(sys.exc_info()[2])
                raise
            finally:
                zope.security.management.endInteraction()
    return middleware

def post_mortem_debug(app, global_conf):
    return PostMortemDebug(app)

def TestApplication(environ, start_response):
    """A simple WSGI app that raises an exception for testing
    purposes.  Nothing to see here."""
    raise RuntimeError('The test application is raising this.')
    start_response('200 OK', [('Content-type', 'text/plain')])
    yield "Test Application"

def test_application_factory(global_config):
    return TestApplication
