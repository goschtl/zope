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

$Id: _app.py,v 1.3 2002/12/26 20:18:07 jim Exp $
"""

import base64
from StringIO import StringIO
from zope.publisher.publish import publish as _publish

__metaclass__ = type

_configured = 0
def config(file):
    "Configure site globals"
    global _configured

    if _configured:
        return

    from zope.configuration.xmlconfig import XMLConfig

    # Set user to system_user, so we can do anything we want
    from zope.security.securitymanagement import system_user
    from zope.security.securitymanagement import newSecurityManager
    newSecurityManager(system_user)

    # Load server-independent site config
    XMLConfig(file)()

    # Reset user
    from zope.security.securitymanagement import noSecurityManager
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
                from zodb.db import DB
                db = DB(storage)
        elif db.endswith(".fs"):
            from zodb.storage.file import FileStorage
            from zodb.db import DB
            storage = FileStorage(db)
            db = DB(storage)

    # XXX When bootstrapping a new database, the following will fail
    #     while trying to add services when no config_file was passed
    #     to Application() below.  So, don't do that. :-)
    from zope.app.startup import bootstrap
    bootstrap.bootstrapInstance(db)

    return db

class Application:

    def __init__(self, db=None, config_file=None):
        if db is None and config_file is None:
            db = 'Data.fs'
            config_file = 'site.zcml'
        
        if config_file is not None:
            config(config_file)
        self.db = database(db)

    def __call__(self):
        from zope.app.publication.zopepublication import ZopePublication
        return self.db.open().root()[ZopePublication.root_name]

    __browser_pub = None
    __TestRequest = None

    def _request(self,
                 path='/', stdin='', stdout=None, basic=None,
                 environment = None, form=None):


        env = {}

        if stdout is None:
            stdout = StringIO()

        if type(stdin) is str:
            stdin = StringIO(stdin)

        p=path.split('?')
        if len(p)==1:
            env['PATH_INFO'] = p[0]
        elif len(p)==2:
            env['PATH_INFO'], env['QUERY_STRING'] = p
        else:
            raise ValueError("Too many ?s in path", path)

        if environment is not None:
            env.update(environment)

        if basic:
            env['HTTP_AUTHORIZATION']="Basic %s" % base64.encodestring(basic)

        if self.__TestRequest is None:
            from zope.publisher.browser import TestRequest
            from zope.app.publication.browser \
                 import BrowserPublication
            from zope.app.publication.zopepublication \
                 import DebugPublication

            class BrowserPublication(DebugPublication, BrowserPublication):
                pass

            self.__TestRequest = TestRequest
            self.__browser_pub = BrowserPublication(self.db)

        request = self.__TestRequest(stdin, stdout, env)
        request.setPublication(self.__browser_pub)
        if form:
            request.update(form)

        return request

    def publish(self, path='/', stdin='', stdout=None, *args, **kw):

        if stdout is None:
            stdout = StringIO()

        request = self._request(path, stdin, stdout, *args, **kw)
        _publish(request)
        stdout.seek(0)
        print stdout.read()

    def run(self, *args, **kw):
        request = self._request(*args, **kw)
        _publish(request, handle_errors = 0)

    def debug(self, *args, **kw):

        import pdb

        class Pdb(pdb.Pdb):
            def do_pub(self,arg):
                if hasattr(self,'done_pub'):
                    print 'pub already done.'
                else:
                    self.do_s('')
                    self.do_s('')
                    self.do_c('')
                    self.done_pub=1
            def do_ob(self,arg):
                if hasattr(self,'done_ob'):
                    print 'ob already done.'
                else:
                    self.do_pub('')
                    self.do_c('')
                    self.done_ob=1

        db=Pdb()

        def fbreak(db, meth):
            try:
                meth = meth.im_func
            except AttributeError:
                pass
            code = meth.func_code
            lineno = getlineno(code)
            filename = code.co_filename
            db.set_break(filename,lineno)

        request = self._request(*args, **kw)
        fbreak(db, _publish)
        fbreak(db, request.publication.call_wrapper.__call__)

##         dbdata = {'breakpoints':(), 'env':env, 'extra': extra}
##         b=''
##         try: b=open('.bobodb','r').read()
##         except: pass
##         if b:
##             exec b in dbdata

##         for b in dbdata['breakpoints']:
##             if isinstance(b, TupleType):
##                 apply(db.set_break, b)
##             else:
##                 fbreak(db,b)

        db.prompt='pdb> '

        print '* Type c<cr> to jump to published object call.'
        db.runcall(_publish, request)

try:
    from codehack import getlineno
except:
    def getlineno(code):
        return code.co_firstlineno
