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
r"""This is a test to make sure that when the input stream is larger then
100000 bytes then the stream is stored in a file on disk and not in memory.

  >>> instance = Instance()
  >>> instance.start()
  >>> instance.wait()

  >>> s = socket.socket()
  >>> s.settimeout(60.0)

  >>> s.connect(('localhost', instance.port))
  >>> s.sendall('GET http://localhost:%s/checkLargeFileUpload HTTP/1.1\r\n'
  ...           % instance.port)
  >>> s.sendall('Content-Length: 120005\r\n')
  >>> s.sendall('Content-Type: text/plain\r\n')
  >>> s.sendall('\r\n')
  >>> s.sendall('xxxxxxxxxx\r\n' * 10000 + 'end\r\n')
  >>> f = s.makefile()

If the input stream is not an instance of twisted.web2.stream.FileStream then
the status line of this request will be 'HTTP/1.1 500 Internal Server Error'.

  >>> f.readline()
  'HTTP/1.1 200 OK\r\n'

  >>> f.close()
  >>> s.close()

  >>> instance.stop()
  >>> shutil.rmtree(instance.dir)

$Id$
"""

import shutil
import socket
from zope.testing import doctest
import test_inputbuffering

class Server(object):

    def __init__(self, _, request):
        self.request = request

    def checkLargeFileUpload(self):
        length = int(self.request.getHeader("content-length"))
        if length != 120005:
            raise ValueError("Content length is wrong.")

        from twisted.web2.stream import FileStream
        ## At this stage wsgi.input is a buffered stream of a buffered stream and
        ## hence .stream.stream.
        innerstream = self.request["wsgi.input"].stream.stream
        if not isinstance(innerstream, FileStream):
            raise ValueError("Input stream is not a FileStream.")

        return "Stream is ok"


class Instance(test_inputbuffering.Instance):

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
            name="checkLargeFileUpload"
            class="zope.app.twisted.tests.test_largeinput.Server"
            attribute="checkLargeFileUpload"
            permission="zope.Public"
            />

        </configure>
        """
        test_inputbuffering.mkfile(self.dir, "site.zcml",
                                   template, self.__dict__)


def test_suite():
    suite = doctest.DocTestSuite()
    suite.level = 2
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest = "test_suite")
