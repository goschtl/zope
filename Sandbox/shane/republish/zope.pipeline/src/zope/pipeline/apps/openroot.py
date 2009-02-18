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

from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IWSGIApplication
from zope.security.checker import ProxyFactory


class RootOpener(object):
    """Puts a root object in 'zope.request' of the WSGI environment.

    Requires the environment to contain 'zope.database',
    which is normally a ZODB.DB.DB object.
    Sets request.traversed to a list with one element.
    Also closes the database connection on the way out.

    Special case: if the traversal stack contains "++etc++process",
    instead of opening the database, this uses the utility by that
    name as the root object.
    """
    implements(IWSGIApplication)

    root_name = 'Application'
    app_controller_name = '++etc++process'

    def __init__(self, next_app, database):
        self.next_app = next_app
        self.database = database

    def __call__(self, environ, start_response):
        request = environ['zope.request']

        # If the traversal stack contains self.app_controller_name,
        # then we should get the app controller rather than look
        # in the database.
        if self.app_controller_name in request.traversal_stack:
            root = getUtility(Interface, name=self.app_controller_name)
            request.traversed = [(self.app_controller_name, root)]
            return self.next_app(environ, start_response)

        # Open the database.
        conn = self.database.open()
        try:
            request.annotations['ZODB.interfaces.IConnection'] = conn
            root = conn.root()
            app = root.get(self.root_name, None)
            if app is None:
                raise SystemError("Zope Application Not Found")
            request.traversed = [(self.root_name, ProxyFactory(app))]

            return self.next_app(environ, start_response)
        finally:
            conn.close()
