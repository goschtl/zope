##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
r"""Meke sure that input is buffered

Meke sure that input is buffered, so that a slow client doesn't block an application thread.


    >>> instance = Instance()
    >>> instance.start()
    >>> instance.wait()

Now, we'll open a socket to it and send a partial request:

    >>> bad = socket.socket()
    >>> bad.connect(('localhost', instance.port))
    >>> bad.sendall('GET http://localhost:%s/echo HTTP/1.1\r\n'
    ...             % instance.port)
    >>> bad.sendall('Content-Length: 10\r\n')
    >>> bad.sendall('Content-Type: text/plain\r\n')
    >>> bad.sendall('\r\n')
    >>> bad.sendall('x')

At this point, the request shouldn't be in a thread yet, so we should be
able to make another request:

    >>> s = socket.socket()
    >>> s.settimeout(60.0)
    >>> s.connect(('localhost', instance.port))
    >>> s.sendall('GET http://localhost:%s/echo HTTP/1.1\r\n'
    ...           % instance.port)
    >>> s.sendall('Content-Length: 10\r\n')
    >>> s.sendall('Content-Type: text/plain\r\n')
    >>> s.sendall('\r\n')
    >>> s.sendall('xxxxxxxxxxxxxxx\n')
    >>> f = s.makefile()
    >>> f.readline()
    'HTTP/1.1 200 OK\r\n'

    >>> message = rfc822.Message(f)
    >>> message['content-length']
    '10'

    >>> s.close()


    >>> bad.sendall('xxxxxxxxxx\n')
    >>> bad.close()
    >>> instance.stop()
    >>> shutil.rmtree(instance.dir)

$Id$
"""
import errno
import httplib
import os
import rfc822
import shutil
import socket
import sys
import tempfile
import time
import unittest
from zope.testing import doctest
import ZEO.tests.testZEO # we really need another library
import ZEO.tests.forker

class Echo:

    def __init__(self, _, request):
        self.request = request

    def echo(self):
        return self.request.bodyStream.read()
    


class Instance:

    def __init__(self, dir=None, name=None, zeo_port=1):
        if dir is None:
            self.dir = tempfile.mkdtemp('zat', 'test')
        else:
            self.dir = os.path.join(dir, name)
            os.mkdir(self.dir)

        self.path = sys.path
        self.python = sys.executable
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

        <page xmlns="http://namespaces.zope.org/browser"
            for="*"
            name="echo"
            class="zope.app.twisted.tests.test_inputbuffering.Echo"
            attribute="echo"
            permission="zope.Public"
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
        <demostorage>
        </demostorage>
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
                  (sys.executable, os.path.join(self.dir, "runzope"), ),
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

    url = property(lambda self: 'http://localhost:%d/' % self.port)
    
def mkfile(dir, name, template, kw):
    f = open(os.path.join(dir, name), 'w')
    f.write(template % kw)
    f.close()
    
def test_suite():
    suite = doctest.DocTestSuite()
    suite.level = 2
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

