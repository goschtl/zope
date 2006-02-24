##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""This file basically contains FTP functional tests.

$Id$
"""
__docformat__="restructuredtext"
from cStringIO import StringIO
import posixpath
import unittest
from datetime import datetime

from twisted.test import test_ftp
from twisted.internet import reactor, protocol, defer
from twisted.protocols import ftp

from zope.app.twisted.ftp.server import FTPRealm, FTPFactory
from zope.app.twisted.ftp.tests.test_publisher import RequestFactory
from zope.app.twisted.ftp.tests import demofs

from twisted.trial.util import wait
from twisted.trial.unittest import TestCase

import test_zopetrial

class DemoFileSystem(demofs.DemoFileSystem):
    def mkdir_nocheck(self, path):
        path, name = posixpath.split(path)
        d = self.getdir(path)
        if name in d.files:
            raise OSError("Already exists:", name)
        newdir = self.Directory()
        newdir.grant(self.user, demofs.read | demofs.write)
        d.files[name] = newdir

    def writefile_nocheck(self, path, instream, start = None,
                          end = None, append = False):
        path, name = posixpath.split(path)
        d = self.getdir(path)
        f = d.files.get(name)
        if f is None:
            d = self.getdir(path)
            f = d.files[name] = self.File()
            f.grant(self.user, demofs.read | demofs.write)
        elif f.type != 'f':
            raise OSError("Can't overwrite a directory")

        if append:
            f.data += instream.read()
        else:
            f.data = instream.read()

class FTPServerTestCase(test_ftp.FTPServerTestCase):
    def tearDown(self):
        ## Uninstall the monkey patches needed to get the tiral tests
        ## running successfully within the zope test runner.
        test_zopetrial.tearDown()

        # Clean up sockets
        self.client.transport.loseConnection()
        d = self.port.stopListening()
        if d is not None:
            wait(d)

        del self.serverProtocol

    def setUp(self):
        ## Install monkey patches in the test_zopetrail module that
        ## allow me to cleanly test the Twisted server code from within
        ## the Zope test runner.
        ## Don't forget to call test_zopetrial.tearDown
        test_zopetrial.setUp()

        root = demofs.Directory()
        # the tuple has a user name is used by ZopeSimpleAuthentication to
        # authenticate users.
        root.grant('root', demofs.write)
        self.rootfs = rootfs = DemoFileSystem(root, ('root', 'root'))

        # Start the server
        self.factory = FTPFactory(request_factory = RequestFactory(rootfs))
        self.port = reactor.listenTCP(0, self.factory, interface="127.0.0.1")

        # Hook the server's buildProtocol to make the protocol instance
        # accessible to tests.
        buildProtocol = self.factory.buildProtocol
        def _rememberProtocolInstance(addr):
            protocol = buildProtocol(addr)
            self.serverProtocol = protocol.wrappedProtocol
            return protocol
        self.factory.buildProtocol = _rememberProtocolInstance

        # Connect a client to it
        portNum = self.port.getHost().port
        clientCreator = protocol.ClientCreator(reactor, ftp.FTPClientBasic)
        self.client = wait(clientCreator.connectTCP("127.0.0.1", portNum))

    def _anonymousLogin(self):
        responseLines = wait(self.client.queueStringCommand('USER anonymous'))
        self.assertEquals(
            ['331 Password required for anonymous.'],
            responseLines
        )

        responseLines = wait(self.client.queueStringCommand(
            'PASS test@twistedmatrix.com')
        )
        self.assertEquals(
            ['230 User logged in, proceed'],
            responseLines
        )

class BasicFTPServerTestCase(FTPServerTestCase,
                             test_ftp.BasicFTPServerTestCase):
    def _authLogin(self):
        responseLines = wait(self.client.queueStringCommand('USER root'))
        self.assertEquals(
            ['331 Password required for root.'],
            responseLines
        )

        responseLines = wait(self.client.queueStringCommand(
            'PASS root')
        )
        self.assertEquals(
            ['230 User logged in, proceed'],
            responseLines
        )

    def testQuit(self):
        # this test is causing we problems. Works on 2.2.X but times out
        # on 2.1.X
        pass

    def test_MKD(self):
        self._authLogin()
        responseLines = wait(self.client.queueStringCommand('MKD /newdir'))
        self.assertEqual(['257 "/newdir" created'], responseLines)

    def test_RMD(self):
        self.rootfs.mkdir_nocheck('/newdir')

        self._authLogin()
        responseLines = wait(self.client.queueStringCommand('RMD /newdir'))
        self.assertEqual(
            ['250 Requested File Action Completed OK'], responseLines)

    def test_DELE(self):
        self.rootfs.writefile_nocheck('/file.txt', StringIO('x' * 20))

        self._authLogin()
        responseLines = wait(self.client.queueStringCommand('DELE /file.txt'))
        self.assertEqual(
            ['250 Requested File Action Completed OK'], responseLines)

    def test_SIZE(self):
        self.rootfs.writefile_nocheck('/file.txt', StringIO('x' * 20))

        self._anonymousLogin()
        responseLines = wait(self.client.queueStringCommand('SIZE /file.txt'))
        self.assertEqual(['213 20'], responseLines)

    def test_SIZE_on_dir(self):
        self._anonymousLogin()
        responseLines = wait(self.client.queueStringCommand('SIZE /'))
        self.assertEqual(['213 0'] , responseLines)

    def test_RENAME(self):
        data = StringIO('x' * 20)
        self.rootfs.writefile('/file.txt', data)

        self._authLogin()
        responseLines = wait(
            self.client.queueStringCommand('RNFR /file.txt'))
        self.assertEqual(
            ['350 Requested file action pending further information.'],
            responseLines)
        responseLines = wait(
            self.client.queueStringCommand('RNTO /newfile.txt'))
        self.assertEqual(
            ['250 Requested File Action Completed OK'], responseLines)

        file = self.rootfs.get('newfile.txt')
        self.assertEqual(file.data, data.getvalue())
        self.assertEqual(['newfile.txt'], self.rootfs.names('/'))

    def test_RENAME_duplicate(self):
        data = StringIO('x' * 20)
        self.rootfs.writefile('/file.txt', data)
        datadest = StringIO('y' * 20)
        self.rootfs.writefile('/newfile.txt', datadest)

        self._authLogin()
        responseLines = wait(
            self.client.queueStringCommand('RNFR /file.txt'))
        self.assertEqual(
            ['350 Requested file action pending further information.'],
            responseLines)
        deferred = self.client.queueStringCommand('RNTO /newfile.txt')
        responseLines = self._waitForCommandFailure(deferred)
        self.assertEqual(
            ['550 /newfile.txt: Permission denied.'], responseLines)

    def test_RENAME_nosource_file(self):
        self._authLogin()

        responseLines = wait(
            self.client.queueStringCommand('RNFR /file.txt'))
        self.assertEqual(
            ['350 Requested file action pending further information.'],
            responseLines)
        deferred = self.client.queueStringCommand('RNTO /newfile.txt')
        responseLines = self._waitForCommandFailure(deferred)
        self.assertEqual(
            ['550 /file.txt: No such file or directory.'], responseLines)



class FTPServerPasvDataConnectionTestCase(FTPServerTestCase,
                                  test_ftp.FTPServerPasvDataConnectionTestCase):

    def testLIST(self):
        # Login
        self._anonymousLogin()

        # Download a listing
        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('LIST')
        wait(defer.gatherResults([d, downloader.d]))

        # No files, so the file listing should be empty
        self.assertEqual('', downloader.buffer)

        # Make some directories
        self.rootfs.mkdir_nocheck('/foo')
        self.rootfs.mkdir_nocheck('/bar')

        # Download a listing again
        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('LIST')
        wait(defer.gatherResults([d, downloader.d]))

        # Now we expect 2 lines because there are two files.
        self.assertEqual(2, len(downloader.buffer[:-2].split('\r\n')))

        # Download a names-only listing
        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('NLST ')
        wait(defer.gatherResults([d, downloader.d]))
        filenames = downloader.buffer[:-2].split('\r\n')
        filenames.sort()
        self.assertEqual(['bar', 'foo'], filenames)

        # Download a listing of the 'foo' subdirectory
        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('LIST foo')
        wait(defer.gatherResults([d, downloader.d]))

        # 'foo' has no files, so the file listing should be empty
        self.assertEqual('', downloader.buffer)

        # Change the current working directory to 'foo'
        wait(self.client.queueStringCommand('CWD foo'))

        # Download a listing from within 'foo', and again it should be empty
        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('LIST')
        wait(defer.gatherResults([d, downloader.d]))
        self.assertEqual('', downloader.buffer)

    def testLIST_with_mtime(self):
        self._anonymousLogin()

        # Set up file with modification date set.
        self.rootfs.writefile_nocheck('/foo', StringIO('x' * 20))
        foo = self.rootfs.get('/foo')
        now = datetime.now()
        foo.modified = now

        # Download a listing for foo.
        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('LIST /foo')
        wait(defer.gatherResults([d, downloader.d]))

        # check the data returned especially the date.
        buf = downloader.buffer[:-2].split('\r\n')
        self.assertEqual(len(buf), 1)
        buf = buf[0]
        buf = buf.split(None, 5)[5]
        self.assertEqual(buf, '%s foo' % now.strftime('%b %d %H:%M'))

    def testLIST_nofile(self):
        self._anonymousLogin()

        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('LIST /foo')
        responseLines = self._waitForCommandFailure(d)

        self.assertEqual(['550 /foo: No such file or directory.'],
                         responseLines)

    def testManyLargeDownloads(self):
        # Login
        self._anonymousLogin()

        # Download a range of different size files
        for size in range(100000, 110000, 500):
            self.rootfs.writefile_nocheck('/%d.txt' % (size,),
                                          StringIO('x' * size))

            downloader = self._makeDataConnection()
            d = self.client.queueStringCommand('RETR %d.txt' % (size,))
            wait(defer.gatherResults([d, downloader.d]))
            self.assertEqual('x' * size, downloader.buffer)


class FTPServerPortDataConnectionTestCaes(FTPServerPasvDataConnectionTestCase,
                                  test_ftp.FTPServerPortDataConnectionTestCase):
    def setUp(self):
        FTPServerPasvDataConnectionTestCase.setUp(self)
        self.dataPorts = []

    def tearDown(self):
        l = [defer.maybeDeferred(port.stopListening) for port in self.dataPorts]
        wait(defer.DeferredList(l, fireOnOneErrback=True))
        return FTPServerPasvDataConnectionTestCase.tearDown(self)

from twisted.test.test_ftp import _BufferingProtocol

class ZopeFTPPermissionTestCases(FTPServerTestCase):
    def setUp(self):
        FTPServerTestCase.setUp(self)
        self.filename = 'nopermissionfolder'
        self.rootfs.writefile('/%s' % self.filename, StringIO('x' * 100))
        file = self.rootfs.get(self.filename)
        file.grant('michael', 0)
        del file.access['anonymous']

    def _makeDataConnection(self):
        # Establish a passive data connection (i.e. client connecting to
        # server).
        responseLines = wait(self.client.queueStringCommand('PASV'))
        host, port = ftp.decodeHostPort(responseLines[-1][4:])
        downloader = wait(
            protocol.ClientCreator(reactor,
                                   _BufferingProtocol).connectTCP('127.0.0.1',
                                                                  port)
        )
        return downloader

    def _michaelLogin(self):
        responseLines = wait(self.client.queueStringCommand('USER michael'))
        self.assertEquals(
            ['331 Password required for michael.'],
            responseLines
        )

        responseLines = wait(self.client.queueStringCommand(
            'PASS michael')
        )
        self.assertEquals(
            ['230 User logged in, proceed'],
            responseLines
        )

    def testNoSuchDirectory(self):
        self._michaelLogin()
        deferred = self.client.queueStringCommand('CWD /nosuchdir')
        failureResponseLines = self._waitForCommandFailure(deferred)
        self.failUnless(failureResponseLines[-1].startswith('550'),
                        "Response didn't start with 550: %r" %
                              failureResponseLines[-1])

    def testListNonPermission(self):
        self._michaelLogin()

        # Download a listing
        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('NLST ')
        wait(defer.gatherResults([d, downloader.d]))

        # No files, so the file listing should be empty
        filenames = downloader.buffer[:-2].split('\r\n')
        filenames.sort()
        self.assertEqual([self.filename], filenames)

    def testRETR_wo_Permission(self):
        self._michaelLogin()

        downloader = self._makeDataConnection()
        d = self.client.queueStringCommand('RETR %s' % self.filename)
        failureResponseLines = self._waitForCommandFailure(d)
        self.failUnless(failureResponseLines[-1].startswith('550'),
                        "Response didn't start with 550: %r" %
                        failureResponseLines[-1])
        if downloader.transport.connected:
            downloader.transport.loseConnection()


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(FTPServerTestCase))
    suite.addTest(unittest.makeSuite(BasicFTPServerTestCase))
    suite.addTest(unittest.makeSuite(FTPServerPasvDataConnectionTestCase))
    suite.addTest(unittest.makeSuite(FTPServerPortDataConnectionTestCaes))
    suite.addTest(unittest.makeSuite(ZopeFTPPermissionTestCases))

    return suite

if __name__ == '__main__':
    test_suite()
