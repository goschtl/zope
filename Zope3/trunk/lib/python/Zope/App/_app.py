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

$Id: _app.py,v 1.5 2002/12/12 20:16:34 gvanrossum Exp $
"""
__metaclass__ = type

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

    # XXX When bootstrapping a new database, the following will fail
    #     while trying to add services when no config_file was passed
    #     to Application() below.  So, don't do that. :-)
    from Zope.App.StartUp import bootstrap
    bootstrap.bootstrapInstance(db)

    return db

class Application:

    def __init__(self, db, config_file=None):
        if config_file is not None:
            config(config_file)
        self.db = database(db)

    def __call__(self):
        return self.db.open().root()['Application']

    __browser_pub = None
    __TestRequest = None

    def debug(self, path='/', stdin='', stdout=None, basic=None, pm=0,
              environment=None, **kw):
        import base64
        from cStringIO import StringIO
        from Zope.Publisher.Publish import publish

        if stdout is None:
            stdout = StringIO()

        if type(stdin) is str:
            stdin = StringIO(stdin)

        env = {'PATH_INFO': path}
        if environment is not None:
            env.update(environment)
        env.update(kw)

        if basic:
            env['HTTP_AUTHORIZATION']="Basic %s" % base64.encodestring(basic)

        if self.__TestRequest is None:
            from Zope.Publisher.Browser.BrowserRequest import TestRequest
            from Zope.App.ZopePublication.Browser.Publication \
                 import BrowserPublication
            self.__TestRequest = TestRequest
            self.__browser_pub = BrowserPublication(self.db)

        request = self.__TestRequest(stdin, stdout, env)
        request.setPublication(self.__browser_pub)

        publish(request, handle_errors= not pm)

        stdout.seek(0)
        print stdout.read()
