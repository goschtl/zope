##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Base class for DAV functional tests.

$Id$
"""
from persistent import Persistent
import transaction
from zope.interface import implements
from zope.app.testing.functional import HTTPTestCase, FunctionalTestSetup
from zope.publisher.http import HTTPRequest
from zope.app.publication.http import HTTPPublication
from zope.app.dav.common import WebDAVRequest, WebDAVPublication

from zope.app.folder import Folder
from zope.app.annotation.interfaces import IAttributeAnnotatable

class Page(Persistent):
    implements(IAttributeAnnotatable)    

class DAVTestCase(HTTPTestCase):

    def createFolders(self, path):
        """createFolders('/a/b/c/d') would traverse and/or create three nested
        folders (a, b, c) and return a tuple (c, 'd') where c is a Folder
        instance at /a/b/c."""
        folder = self.getRootFolder()
        if path[0] == '/':
            path = path[1:]
        path = path.split('/')
        for id in path[:-1]:
            try:
                folder = folder[id]
            except KeyError:
                folder[id] = Folder()
                folder = folder[id]
        return folder, path[-1]

    def createObject(self, path, obj):
        folder, id = self.createFolders(path)
        folder[id] = obj
        transaction.commit()

    def addPage(self, path, content):
        page = Page()
        page.source = content
        self.createObject(path, page)

    def makeRequest(self, path = '', basic = None, form = None, env = {},
                    instream = None):
        method = env.get('REQUEST_METHOD', '')

        if instream is None:
            instream = ''

        environment = {"HTTP_HOST": 'localhost',
                       "HTTP_REFERER": 'localhost'}
        environment.update(env)

        app = FunctionalTestSetup().getApplication()
        if method in ('PROPFIND', 'PROPPATCH', 'MKCOL', 'LOCK', 'UNLOCK',
                      'COPY', 'MOVE'):
            request = app._request(path, instream,
                                   environment = environment,
                                   basic = basic, form = form,
                                   request = WebDAVRequest,
                                   publication = WebDAVPublication)
        else:
            request = app._request(path, instream,
                                   environment=environment,
                                   basic=basic, form=form,
                                   request=HTTPRequest,
                                   publication=HTTPPublication)

        return request
