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

$Id$
"""

import base64, time
from StringIO import StringIO
from zope.publisher.publish import publish as _publish, debug_call
from zope.publisher.browser import TestRequest
from zope.app.publication.browser import BrowserPublication
from zope.security.interfaces import IParticipation
from zope.security.management import system_user
from zope.interface import implements

__metaclass__ = type


class SystemConfigurationParticipation:
    implements(IParticipation)

    principal = system_user
    interaction = None


_configured = 0
def config(file, execute=True):
    "Configure site globals"
    global _configured

    if _configured:
        return

    from zope.configuration import xmlconfig

    # Set user to system_user, so we can do anything we want
    from zope.security.management import newInteraction
    newInteraction(SystemConfigurationParticipation())

    # Load server-independent site config
    context = xmlconfig.file(file, execute=execute)

    # Reset user
    from zope.security.management import endInteraction
    endInteraction()

    _configured = execute

    return context

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
                db = DB(storage, cache_size=4000)
        elif db.endswith(".fs"):
            from ZODB.FileStorage import FileStorage
            from ZODB.DB import DB
            storage = FileStorage(db)
            db = DB(storage, cache_size=4000)

    # The following will fail unless the application has been configured.
    from zope.app.process import event
    from zope.app.event import publish
    publish(None, event.DatabaseOpened(db))

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
        """Get the top-level application object

        The object returned is connected to an open database connection.
        """

        from zope.app.publication.zopepublication import ZopePublication
        return self.db.open().root()[ZopePublication.root_name]

    def _request(self,
                 path='/', stdin='', stdout=None, basic=None,
                 environment = None, form=None,
                 request=TestRequest, publication=BrowserPublication):
        """Create a request
        """

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


        pub = publication(self.db)

        request = request(stdin, stdout, env)
        request.setPublication(pub)
        if form:
            # This requires that request class has an attribute 'form'
            # (BrowserRequest has, TestRequest hasn't)
            request.form.update(form)

        return request

    def publish(self, path='/', stdin='', stdout=None, *args, **kw):
        t, c = time.time(), time.clock()

        if stdout is None:
            stdout = StringIO()

        request = self._request(path, stdin, stdout, *args, **kw)
        getStatus = getattr(request.response, 'getStatus', lambda: None)
        _publish(request)
        stdout.seek(0)
        print stdout.read()
        return time.time()-t, time.clock()-c, getStatus()

    def run(self, *args, **kw):
        t, c = time.time(), time.clock()
        request = self._request(*args, **kw)
        getStatus = getattr(request.response, 'getStatus', lambda: None)
        _publish(request, handle_errors=False)
        return time.time()-t, time.clock()-c, getStatus()

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

        request = self._request(*args, **kw)
        fbreak(db, _publish)
        fbreak(db, debug_call)

        print '* Type c<cr> to jump to published object call.'
        db.runcall(_publish, request)


def fbreak(db, meth):
    try:
        meth = meth.im_func
    except AttributeError:
        pass
    code = meth.func_code
    lineno = getlineno(code)
    filename = code.co_filename
    db.set_break(filename,lineno)



try:
    from codehack import getlineno
except:
    def getlineno(code):
        return code.co_firstlineno
