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

from twisted.trial.unittest import TestCase


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
        # Twisted trial has a habit of leaving threads lying about when run
        # from within the Zope test runner - do_cleanThreads removes them.
        # The threads don't actaully cause any errors - they just print
        # out a few extra lines of information when running the tests.
        from twisted.trial import util
        util._Janitor.do_cleanThreads()

        # Clean up sockets
        self.client.transport.loseConnection()
        d = defer.maybeDeferred(self.port.stopListening)
        d.addCallback(self.ebCallback)

        return d

    def ebCallback(self, ignore):
        del self.serverProtocol

    def setUp(self):
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
        d1 = defer.Deferred()
        def _rememberProtocolInstance(addr):
            protocol = buildProtocol(addr)
            self.serverProtocol = protocol.wrappedProtocol
            d1.callback(None)
            return protocol
        self.factory.buildProtocol = _rememberProtocolInstance

        # Connect a client to it
        portNum = self.port.getHost().port
        clientCreator = protocol.ClientCreator(reactor, ftp.FTPClientBasic)
        d2 = clientCreator.connectTCP("127.0.0.1", portNum)
        def gotClient(client):
            self.client = client
        d2.addCallback(gotClient)
        return defer.gatherResults([d1, d2])

    def _anonymousLogin(self):
        d = self.assertCommandResponse(
            'USER anonymous',
            ['331 Password required for anonymous.'])
        return self.assertCommandResponse(
            'PASS test@twistedmatrix.com',
            ['230 User logged in, proceed'],
            chainDeferred = d)


class BasicFTPServerTestCase(FTPServerTestCase,
                             test_ftp.BasicFTPServerTestCase):
    def _authLogin(self):
        d = self.assertCommandResponse(
            'USER root',
            ['331 Password required for root.'])
        return self.assertCommandResponse(
            'PASS root',
            ['230 User logged in, proceed'],
            chainDeferred = d)

    def test_MKD(self):
        d = self._authLogin()
        return self.assertCommandResponse(
            'MKD /newdir',
            ['257 "/newdir" created'],
            chainDeferred = d)

    def test_RMD(self):
        self.rootfs.mkdir_nocheck('/newdir')

        d = self._authLogin()
        return self.assertCommandResponse(
            'RMD /newdir',
            ['250 Requested File Action Completed OK'],
            chainDeferred = d)

    def test_DELE(self):
        self.rootfs.writefile_nocheck('/file.txt', StringIO('x' * 20))

        d = self._authLogin()
        return self.assertCommandResponse(
            'DELE /file.txt',
            ['250 Requested File Action Completed OK'],
            chainDeferred = d)

    def test_SIZE(self):
        self.rootfs.writefile_nocheck('/file.txt', StringIO('x' * 20))
        d = self._anonymousLogin()
        return self.assertCommandResponse(
            'SIZE /file.txt',
            ['213 20'],
            chainDeferred = d)

    def test_SIZE_on_dir(self):
        d = self._anonymousLogin()
        return self.assertCommandResponse(
            'SIZE /',
            ['213 0'],
            chainDeferred = d)

    def test_RENAME(self):
        data = StringIO('x' * 20)
        self.rootfs.writefile('/file.txt', data)

        d = self._authLogin()
        d = self.assertCommandResponse(
            'RNFR /file.txt',
            ['350 Requested file action pending further information.'],
            chainDeferred = d)
        d = self.assertCommandResponse(
            'RNTO /newfile.txt',
            ['250 Requested File Action Completed OK'],
            chainDeferred = d)

        def assertFileStatus(result):
            file = self.rootfs.get('newfile.txt')
            self.assertEqual(file.data, data.getvalue())
            self.assertEqual(['newfile.txt'], self.rootfs.names('/'))

        d.addCallback(assertFileStatus)
        return d

    def test_RENAME_duplicate(self):
        data = StringIO('x' * 20)
        self.rootfs.writefile('/file.txt', data)
        datadest = StringIO('y' * 20)
        self.rootfs.writefile('/newfile.txt', datadest)

        d = self._authLogin()
        d = self.assertCommandResponse(
            'RNFR /file.txt',
            ['350 Requested file action pending further information.'],
            chainDeferred = d)
        d = self.assertCommandFailed(
            'RNTO /newfile.txt',
            ['550 /newfile.txt: Permission denied.'],
            chainDeferred = d)
        return d

    def test_RENAME_nosource_file(self):
        d = self._authLogin()

        d = self.assertCommandResponse(
            'RNFR /file.txt',
            ['350 Requested file action pending further information.'],
            chainDeferred = d)
        d = self.assertCommandFailed(
            'RNTO /newfile.txt',
            ['550 /file.txt: No such file or directory.'],
            chainDeferred = d)
        return d


class FTPServerPasvDataConnectionTestCase(FTPServerTestCase,
                                  test_ftp.FTPServerPasvDataConnectionTestCase):

    def testTwoDirLIST(self):
        # Login
        d = self._anonymousLogin()

        # Make some directories
        self.rootfs.mkdir_nocheck('/foo')
        self.rootfs.mkdir_nocheck('/bar')

        self._download('LIST', chainDeferred = d)
        def checkDownload(download):
            # Now we expect 2 lines because there are two files.
            self.assertEqual(2, len(download[:-2].split('\r\n')))
        d.addCallback(checkDownload)

        # Download a names-only listing
        self._download('NLST ', chainDeferred = d)
        def checkDownload(download):
            filenames = download[:-2].split('\r\n')
            filenames.sort()
            self.assertEqual(['bar', 'foo'], filenames)
        d.addCallback(checkDownload)

        # Download a listing of the 'foo' subdirectory.  'foo' has no files, so
        # the file listing should be empty.
        self._download('LIST foo', chainDeferred = d)
        def checkDownload(download):
            # 'foo' has no files, so the file listing should be empty
            self.assertEqual('', download)
        d.addCallback(checkDownload)

        # Change the current working directory to 'foo'
        def chdir(ignored):
            return self.client.queueStringCommand('CWD foo')
        d.addCallback(chdir)

        # Download a listing from within 'foo', and again it should be empty
        self._download('LIST', chainDeferred = d)
        def checkDownload(download):
            self.assertEqual('', download)
        d.addCallback(checkDownload)
        return d

    def testManyLargeDownloads(self):
        # Login
        d = self._anonymousLogin()

        # Download a range of different size files
        for size in range(100000, 110000, 500):
            self.rootfs.writefile_nocheck('/%d.txt' % (size,),
                                          StringIO('x' * size))

            self._download('RETR %d.txt' % (size,), chainDeferred = d)
            def checkDownload(download, size = size):
                self.assertEqual('x' * size, download)
            d.addCallback(checkDownload)
        return d

    def testLIST_with_mtime(self):
        d = self._anonymousLogin()

        # Set up file with modification date set.
        self.rootfs.writefile_nocheck('/foo', StringIO('x' * 20))
        foo = self.rootfs.get('/foo')
        now = datetime.now()
        foo.modified = now

        # Download a listing for foo.
        self._download('LIST /foo', chainDeferred = d)
        def checkDownload(download):
            # check the data returned especially the date.
            buf = download[:-2].split('\r\n')
            self.assertEqual(len(buf), 1)
            buf = buf[0]
            buf = buf.split(None, 5)[5]
            self.assertEqual(buf, '%s foo' % now.strftime('%b %d %H:%M'))
        return d.addCallback(checkDownload)

    def testLIST_nofile(self):
        d = self._anonymousLogin()

        def queueCommand(ignored):
            d1 = self._makeDataConnection()
            d2 = self.client.queueStringCommand('LIST /foo')
            self.assertFailure(d2, ftp.CommandFailed)
            def failed(exception):
                self.assertEqual(['550 /foo: No such file or directory.'],
                                 exception.args[0])
            d2.addCallback(failed)

            return defer.gatherResults([d1, d2])

        d.addCallback(queueCommand)
        return d


class FTPServerPortDataConnectionTestCaes(FTPServerPasvDataConnectionTestCase,
                                  test_ftp.FTPServerPortDataConnectionTestCase):
    def setUp(self):
        self.dataPorts = []
        return FTPServerPasvDataConnectionTestCase.setUp(self)

    def tearDown(self):
        l = [defer.maybeDeferred(port.stopListening) for port in self.dataPorts]
        d = defer.maybeDeferred(
            FTPServerPasvDataConnectionTestCase.tearDown, self)
        l.append(d)
        return defer.DeferredList(l, fireOnOneErrback = True)


class ZopeFTPPermissionTestCases(FTPServerTestCase):

    def setUp(self):
        def runZopePermSetup(ignored):
            self.filename = 'nopermissionfolder'
            self.rootfs.writefile('/%s' % self.filename, StringIO('x' * 100))
            file = self.rootfs.get(self.filename)
            file.grant('michael', 0)
            del file.access['anonymous']

        return FTPServerTestCase.setUp(self).addCallback(runZopePermSetup)

    def _makeDataConnection(self, ignored = None):
        # Establish a passive data connection (i.e. client connecting to
        # server).
        d = self.client.queueStringCommand('PASV')
        def gotPASV(responseLines):
            host, port = ftp.decodeHostPort(responseLines[-1][4:])
            cc = protocol.ClientCreator(reactor, test_ftp._BufferingProtocol)
            return cc.connectTCP('127.0.0.1', port)
        return d.addCallback(gotPASV)

    def _download(self, command, chainDeferred=None):
        if chainDeferred is None:
            chainDeferred = defer.succeed(None)

        chainDeferred.addCallback(self._makeDataConnection)
        def queueCommand(downloader):
            # wait for the command to return, and the download connection to be
            # closed.
            d1 = self.client.queueStringCommand(command)
            d2 = downloader.d
            return defer.gatherResults([d1, d2])
        chainDeferred.addCallback(queueCommand)

        def downloadDone((ignored, downloader)):
            return downloader.buffer
        return chainDeferred.addCallback(downloadDone)

    def _michaelLogin(self):
        d = self.assertCommandResponse(
            'USER michael',
            ['331 Password required for michael.'])
        return self.assertCommandResponse(
            'PASS michael',
            ['230 User logged in, proceed'],
            chainDeferred = d)

    def testNoSuchDirectory(self):
        d = self._michaelLogin()
        return self.assertCommandFailed(
            'CWD /nosuchdir',
            ['550 /nosuchdir: Permission denied.'],
            chainDeferred = d)

    def testListNonPermission(self):
        d = self._michaelLogin()

        self._download('NLST ', chainDeferred = d)
        def checkDownload(download):
            # No files, so the file listing should be empty
            filenames = download[:-2].split('\r\n')
            filenames.sort()
            self.assertEqual([self.filename], filenames)
        return d.addCallback(checkDownload)

    def testRETR_wo_Permission(self):
        d = self._michaelLogin()

        def queueCommand(ignored):
            d1 = self._makeDataConnection()
            d2 = self.client.queueStringCommand('RETR %s' % self.filename)
            self.assertFailure(d2, ftp.CommandFailed)
            def failed(exception):
                self.assertEqual(
                    ['550 nopermissionfolder: No such file or directory.'],
                    exception.args[0])
            d2.addCallback(failed)

            return defer.gatherResults([d1, d2])

        return d.addCallback(queueCommand)


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
