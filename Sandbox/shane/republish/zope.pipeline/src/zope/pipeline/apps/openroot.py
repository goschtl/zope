##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import re

from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IWSGIApplication
from zope.security.checker import ProxyFactory

from zope.pipeline.envkeys import REQUEST_KEY
from zope.pipeline.envkeys import TRAVERSED_KEY


class RootOpener(object):
    """Establishes the traversal root in the WSGI environment.

    Opens the database, finds the Zope application root, puts a
    security proxy on the root object, and sets
    'zope.pipeline.traversed' in the environment to a list with one
    element containing (root_name, root). If the environment contains
    'zope.pipeline.request', an annotation is added to the request.
    Also closes the database connection on the way out.

    Special case: if the PATH_INFO contains "++etc++process", instead
    of opening the database, this uses the utility by that name as the
    root object.
    """
    implements(IWSGIApplication)

    root_name = 'Application'
    app_controller_name = '++etc++process'
    use_app_controller_re = re.compile('/[+][+]etc[+][+]process(/|$)')

    def __init__(self, next_app, database):
        self.next_app = next_app
        self.database = database
        self.proxy_factory = ProxyFactory

    def __call__(self, environ, start_response):
        # If the PATH_INFO contains the app controller name,
        # then we should use the app controller rather than open
        # the database.
        path = environ.get('PATH_INFO', '')
        if self.use_app_controller_re.search(path) is not None:
            root = getUtility(Interface, name=self.app_controller_name)
            environ[TRAVERSED_KEY] = [(self.app_controller_name, root)]
            return self.next_app(environ, start_response)

        # Open the database.
        conn = self.database.open()
        try:
            request = environ.get(REQUEST_KEY)
            if request is not None:
                request.annotations['ZODB.interfaces.IConnection'] = conn
            root = conn.root()
            app = root.get(self.root_name, None)
            if app is None:
                raise SystemError("Zope Application Not Found")
            environ[TRAVERSED_KEY] = [
                (self.root_name, self.proxy_factory(app))]

            return self.next_app(environ, start_response)
        finally:
            conn.close()
