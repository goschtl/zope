##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""Code to initialize the application server

$Id: _app.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""
__metaclass__ = type

from cStringIO import StringIO
from Zope.Publisher.Publish import publish as _publish

_configured = 0
def config(file):
    "Configure site globals"
    global _configured

    if _configured:
        return

    from Zope.Configuration.xmlconfig import XMLConfig

    # Set user to system_user, so we can do anything we want
    from Zope.Security.SecurityManagement import system_user
    from Zope.Security.SecurityManagement import newSecurityManager
    newSecurityManager(system_user)

    # Load server-independent site config
    XMLConfig(file)()

    # Reset user
    from Zope.Security.SecurityManagement import noSecurityManager
    noSecurityManager()

    _configured = 1

def database(db):
    if type(db) is str:
        # Database name
        if db.endswith('.py'):
            # Python source, exec it
            globals = {}
            execfile(db, globals)
            if 'DB' in globals:
                db = globals['DB']
            else:
                storage = globals['Storage']
                from ZODB.DB import DB
                db = DB(storage)
        elif db.endswith(".fs"):
            from ZODB.FileStorage import FileStorage
            from ZODB.DB import DB
            storage = FileStorage(db)
            db = DB(storage)
    return db

class Application:

    def __init__(self, db, config_file=None):
        if config_file is not None:
            config(config_file)
        self.db = database(db)

        # Make sure we have an Application object
        root = self.db.open().root()
        if 'Application' not in root:
            from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
            from Transaction import get_transaction
            root['Application'] = RootFolder()
            get_transaction().commit()
            root._p_jar.close()

    def __call__(self):
        return self.db.open().root()['Application']

    __browser_pub = None
    __TestRequest = None

    def debug(self, path='/', stdin='', basic=None, **kw):
        out = StringIO()
        if type(stdin) is str:
            stdin = StringIO(stdin)
        env = {'PATH_INFO': path}
        env.update(kw)

        if basic:
            env['HTTP_AUTHORIZATION']="Basic %s" % base64.encodestring(basic)

        if self.__TestRequest is None:
            from Zope.Publisher.Browser.BrowserRequest import TestRequest
            from Zope.App.ZopePublication.Browser.Publication \
                 import BrowserPublication
            self.__TestRequest = TestRequest
            self.__browser_pub = BrowserPublication(self.db)

        request = self.__TestRequest(StringIO(''), StringIO(), env)
        request.setPublication(self.__browser_pub)

        _publish(request, 0)

        out.seek(0)
        print out.read()
        
