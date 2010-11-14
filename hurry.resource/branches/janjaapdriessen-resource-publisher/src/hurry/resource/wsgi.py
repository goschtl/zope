import webob

NEEDED = 'hurry.resource.needed'
PUBLISHER_PREFIX = 'hurry.resource.publisher_prefix'


# TODO: would be nice to make middleware smarter so it could work with
# a streamed HTML body instead of serializing it out to body. That
# would complicate the middleware signicantly, however. We would for
# instance need to recalculate content_length ourselves.

class InjectMiddleWare(object):

    def __init__(self, application, publisher_prefix=None):
        self.application = application
        self.publisher_prefix = publisher_prefix

    def __call__(self, environ, start_response):
        request = webob.Request(environ)

        if self.publisher_prefix is not None:
            # Inform the wrapped application of the presence of a resource
            # publisher and resource URLs may thus be routed to this publisher.
            environ[PUBLISHER_PREFIX] = self.publisher_prefix

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
    return InjectMiddleWare(app, **local_config)
