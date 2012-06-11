##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
r"""Test that ZEO is handled correctly.

This is a rather evil test that involves setting up a real ZEO server
and some clients. We'll borrow some evil infrastructure from ZEO to do
this.

We'll start by setting up and starting a ZEO server.  

    >>> zeo_port = ZEO.tests.testZEO.get_port()
    >>> zconf = ZEO.tests.forker.ZEOConfig(('', zeo_port))
    >>> zport, adminaddr, pid, path = ZEO.tests.forker.start_zeo_server(
    ...     '<demostorage 1>\n</demostorage>\n', zconf, zeo_port)

We'll set up and start two Zope servers that are clients of the
storage server:

    >>> instance_dir = tempfile.mkdtemp('zeo', 'test')
    >>> inst1 = Instance(instance_dir, '1', zeo_port)
    >>> inst1.start()
    >>> inst1.wait()

(Note that we wait for the first server to start before starting the second,
 so that it has a chance to initialize the database.)

    >>> inst2 = Instance(instance_dir, '2', zeo_port)
    >>> inst2.start()

Lets visit the public view of the top folder for both servers.
Before we make each of these calls, we'll wait for the server to
come up:

    >>> print inst1.main_page()
    <...
    <table ...
        <thead> 
          <tr>
            ...
            <th>Name</th>
            <th>Title</th>
            <th>Created</th>
            <th>Modified</th>
            ...

    >>> inst2.wait()
    >>> print inst2.main_page()
    <...
    <table ...
        <thead> 
          <tr>
            ...
            <th>Name</th>
            <th>Title</th>
            <th>Created</th>
            <th>Modified</th>
            ...

Now, if we add a folder on one server, it should appear on the other:

    >>> from zope.testbrowser.browser import Browser
    >>> browser = Browser()
    >>> browser.open(inst1.url + '@@contents.html')
    >>> browser.getLink('Folder').click()
    >>> browser.getControl(name='new_value').value = 'newfolder'
    >>> browser.getControl('Apply').click()

    >>> 'newfolder' in inst1.main_page()
    True

    >>> 'newfolder' in inst2.main_page()
    True

Note that we use main_page because testbrowser, unfortunately, asks for
robots.txt on every request.  This defeats the test we are trying to
do here. Why?  The original symptom was that, when a change was made
on one ZEO client, then the change wouldn't be seen on the other
client on the first request. Subsequent requests would see the change
because ZODB syncs the storages at the end of each transaction.  The
request for robots.txt causes the database to sync, which prevents us
from seeing the bug.

Cleanup:

    >>> browser.mech_browser.close() # TODO: Browser needs close.
    >>> inst1.stop()
    >>> inst2.stop()
    >>> ZEO.tests.forker.shutdown_zeo_server(('localhost', zeo_port))
    >>> shutil.rmtree(instance_dir)

$Id$
"""
import asyncore
import errno
import httplib
import os
import sys
import shutil
import socket
import tempfile
import time
import unittest
from zope.testing import doctest
import ZEO.tests.testZEO
import ZEO.tests.forker

class Instance:

    def __init__(self, dir=None, name=None, zeo_port=1):
        if dir is None:
            self.dir = tempfile.mkdtemp('zeo', 'test')
        else:
            self.dir = os.path.join(dir, name)
            os.mkdir(self.dir)

        self.path = sys.path
        self.config = os.path.join(self.dir, 'zope.conf')
        self.zeo_port = zeo_port
        self.port = ZEO.tests.testZEO.get_port()
        #print >> sys.stderr, 'port', self.port
        self.socket = os.path.join(self.dir, 'socket')
        self.z3log = os.path.join(self.dir, 'z3.log')
        self.accesslog = os.path.join(self.dir, 'access.log')
        self.sitezcml = os.path.join(self.dir, 'site.zcml')
        for file in self.files:
            getattr(self, file)()

    files = 'runzope', 'site_zcml', 'zope_conf'

    def runzope(self):
        template = """
        import sys
        sys.path[:] = %(path)r
        from zope.app.twisted.main import main
        main(["-C", %(config)r] + sys.argv[1:])
        """
        template = '\n'.join([l.strip() for l in template.split('\n')])
        mkfile(self.dir, "runzope", template, self.__dict__)

    def site_zcml(self):
        template = """
        <configure xmlns="http://namespaces.zope.org/zope">

        <include package="zope.app" />
        <include package="zope.app.twisted" />
        <securityPolicy
            component="zope.security.simplepolicies.PermissiveSecurityPolicy" />
        
        <unauthenticatedPrincipal
            id="zope.anybody"
            title="Unauthenticated User" />
        
        <principal
            id="zope.manager"
            title="Manager"
            login="jim"
            password="123"
            />
        
        </configure>
        """
        mkfile(self.dir, "site.zcml", template, self.__dict__)

    def zope_conf(self):
        template = """
        site-definition %(sitezcml)s
        threads 1
        <server>
          type HTTP
          address localhost:%(port)s
        </server>
        <zodb>
        <zeoclient>
          server localhost:%(zeo_port)s
          storage 1
          cache-size 20MB
        </zeoclient>
        </zodb>
        <accesslog>
          <logfile>
            path %(accesslog)s
          </logfile>
        </accesslog>
        <eventlog>
          <logfile>
            path %(z3log)s
          </logfile>
        </eventlog>
        """
        mkfile(self.dir, "zope.conf", template, self.__dict__)

    def start(self):
        os.spawnv(os.P_NOWAIT, sys.executable,
                  (sys.executable, '-Wignore',
                   os.path.join(self.dir, "runzope"), ),
                  )
                  
    def stop(self):
        connection = httplib.HTTPConnection('localhost', self.port)
        connection.request(
            'POST',
            self.url + '++etc++process/servercontrol.html',
            'time%3Aint=0&shutdown=Shutdown%20server',
            {'Content-Type': 'application/x-www-form-urlencoded'},
            )
        response = connection.getresponse()
        connection.close()
        self.waittodie()

    def main_page(self):
        connection = httplib.HTTPConnection('localhost', self.port)
        connection.request('GET', self.url)
        response = connection.getresponse()
        if response.status != 200:
            raise AssertionError(response.status)
        body = response.read()
        connection.close()
        return body

    def wait(self):
        addr = 'localhost', self.port
        for i in range(120):
            time.sleep(0.25)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(addr)
                s.close()
                break
            except socket.error, e:
                if e[0] not in (errno.ECONNREFUSED, errno.ECONNRESET):
                    raise
                s.close()

    def waittodie(self):
        addr = 'localhost', self.port
        for i in range(120):
            time.sleep(0.25)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(addr)
                s.close()
            except socket.error, e:
                if e[0] not in (errno.ECONNREFUSED, errno.ECONNRESET):
                    raise
                s.close()
                break

    url = property(lambda self: 'http://localhost:%d/' % self.port)
    
def mkfile(dir, name, template, kw):
    f = open(os.path.join(dir, name), 'w')
    f.write(template % kw)
    f.close()
        
def test_suite():
    suite = doctest.DocTestSuite(
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        )
    suite.level = 2
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

