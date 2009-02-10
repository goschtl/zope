
"""

Rules:

    * __getitem__ all path elements except ++, @@, maybe +
    * Look up a view at the end using getMultiAdapter().
    * If the view has a capitalized method name matching REQUEST_METHOD,
      traverse to that.
"""

class SimpleTraverser(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        