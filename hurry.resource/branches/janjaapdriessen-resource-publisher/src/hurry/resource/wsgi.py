import webob
import hurry.resource

NEEDED = 'hurry.resource.needed'

# TODO: would be nice to make middleware smarter so it could work with
# a streamed HTML body instead of serializing it out to body. That
# would complicate the middleware signicantly, however. We would for
# instance need to recalculate content_length ourselves.

class InjectMiddleWare(object):

    def __init__(self, application, signature):
        self.application = application

    def __call__(self, environ, start_response):
        request = webob.Request(environ)

        # XXX the needed inclusions object is created here and the
        # signature should be set on it as would the mode and dev_mode
        # etcetera.

        # Get the response from the wrapped application:
        response = request.get_response(self.application)

        # Post-process the response:
        # We only continue if the content-type is appropriate.
        if not response.content_type.lower() in ['text/html', 'text/xml']:
            return response(environ, start_response)

        # The wrapped application may have left information in the environment
        # about needed inclusions.
        needed = response.environ.get(NEEDED)
        if needed is not None:
            response.body = needed.render_topbottom_into_html(response.body)
        return response(environ, start_response)

def make_inject(app, global_config, **local_config):
    return InjectMiddleWare(
        app, hurry.resource.publisher_signature, **local_config)
