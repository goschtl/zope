


class SimpleTraverser(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        