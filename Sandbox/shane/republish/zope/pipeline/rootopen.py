
from zope.component import getUtility
from zope.interface import adapts
from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication
from zope.security.checker import ProxyFactory


class RootOpener(object):
    """Puts a root object in 'zope.request' of the WSGI environment.

    Sets request.traversed to a list with one element.
    Also closes the database connection on the way out.

    Special case: if the traversal stack contains "++etc++process",
    instead of opening the database, this uses the utility by that
    name as the root object.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication, IZopeConfiguration)

    database_name = 'main'
    root_name = 'Application'
    app_controller_name = '++etc++process'

    def __init__(self, app, zope_conf):
        self.app = app
        self.db = zope_conf.databases[self.database_name]

    def __call__(self, environ, start_response):
        request = environ['zope.request']

        # If the traversal stack contains self.app_controller_name,
        # then we should get the app controller rather than look
        # in the database.
        if self.app_controller_name in request.traversal_stack:
            root = getUtility(name=self.app_controller_name)
            request.traversed = [(self.app_controller_name, root)]
            return self.app(environ, start_response)

        # Open the database.
        conn = self.db.open()

        request.annotations['ZODB.interfaces.IConnection'] = conn
        root = conn.root()
        app = root.get(self.root_name, None)
        if app is None:
            raise SystemError("Zope Application Not Found")

        request.traversed = [(self.root_name, ProxyFactory(app))]

        try:
            return self.app(environ, start_response)
        finally:
            conn.close()
