##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: testFTPServer.py,v 1.5 2002/12/20 09:49:23 srichter Exp $
"""

import unittest
import tempfile
import os
from asyncore import socket_map, poll
import socket
import shutil
from types import StringType
from StringIO import StringIO

from threading import Thread
from Zope.Server.TaskThreads import ThreadedTaskDispatcher
from Zope.Server.FTP.FTPServer import FTPServer
from Zope.Server.FTP.FTPStatusMessages import status_msgs
from Zope.Server.Adjustments import Adjustments
from Zope.Server.ITask import ITask

from Zope.Server.VFS.OSFileSystem import OSFileSystem
from Zope.Server.FTP.TestFilesystemAccess import TestFilesystemAccess

import ftplib

from time import sleep, time

td = ThreadedTaskDispatcher()

LOCALHOST = '127.0.0.1'
SERVER_PORT = 0      # Set these port numbers to 0 to auto-bind, or
CONNECT_TO_PORT = 0  # use specific numbers to inspect using TCPWatch.


my_adj = Adjustments()


def retrlines(ftpconn, cmd):
    res = []
    ftpconn.retrlines(cmd, res.append)
    return ''.join(res)


class Tests(unittest.TestCase):

    def setUp(self):
        td.setThreadCount(1)
        self.orig_map_size = len(socket_map)

        self.root_dir = tempfile.mktemp()
        os.mkdir(self.root_dir)
        os.mkdir(os.path.join(self.root_dir, 'test'))

        fs = OSFileSystem(self.root_dir)
        fs_access = TestFilesystemAccess(fs)

        self.server = FTPServer(LOCALHOST, SERVER_PORT, fs_access,
                                task_dispatcher=td, adj=my_adj)
        if CONNECT_TO_PORT == 0:
            self.port = self.server.socket.getsockname()[1]
        else:
            self.port = CONNECT_TO_PORT
        self.run_loop = 1
        self.counter = 0
        self.thread = Thread(target=self.loop)
        self.thread.start()
        sleep(0.1)  # Give the thread some time to start.


    def tearDown(self):
        self.run_loop = 0
        self.thread.join()
        td.shutdown()
        self.server.close()
        # Make sure all sockets get closed by asyncore normally.
        timeout = time() + 2
        while 1:
            if len(socket_map) == self.orig_map_size:
                # Clean!
                break
            if time() >= timeout:
                self.fail('Leaked a socket: %s' % `socket_map`)
                break
            poll(0.1, socket_map)

        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)

    def loop(self):
        import select
        from errno import EBADF
        while self.run_loop:
            self.counter = self.counter + 1
            # print 'loop', self.counter
            try:
                poll(0.1, socket_map)
            except select.error, data:
                if data[0] == EBADF:
                    print "exception polling in loop(): ", data
                else:
                    raise

    def getFTPConnection(self, login=1):
        ftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ftp.connect((LOCALHOST, self.port))
        result = ftp.recv(10000).split()[0]
        self.assertEqual(result, '220')
        if login:
            ftp.send('USER foo\r\n')
            self.assertEqual(ftp.recv(1024),
                             status_msgs['PASS_REQUIRED'] +'\r\n')
            ftp.send('PASS bar\r\n')
            self.assertEqual(ftp.recv(1024),
                             status_msgs['LOGIN_SUCCESS'] +'\r\n')

        return ftp


    def execute(self, commands, login=1):
        ftp = self.getFTPConnection(login)

        try:
            if type(commands) is StringType:
                commands = (commands,)

            for command in commands:
                ftp.send('%s\r\n' %command)
                result = ftp.recv(10000)

            self.failUnless(result.endswith('\r\n'))
        finally:
            ftp.close()
        return result.split('\r\n')[0]


    def testABOR(self):
        self.assertEqual(self.execute('ABOR', 1),
                         status_msgs['TRANSFER_ABORTED'])


    def testCDUP(self):
        self.assertEqual(self.execute(('CWD test', 'CDUP'), 1),
                         status_msgs['SUCCESS_250'] %'CDUP')
        self.assertEqual(self.execute('CDUP', 1),
                         status_msgs['SUCCESS_250'] %'CDUP')


    def testCWD(self):
        self.assertEqual(self.execute('CWD test', 1),
                         status_msgs['SUCCESS_250'] %'CWD')
        self.assertEqual(self.execute('CWD foo', 1),
                         status_msgs['ERR_NO_DIR'] %'/foo')


    def testDELE(self):
        open(os.path.join(self.root_dir, 'foo'), 'w').write('blah')
        self.assertEqual(self.execute('DELE foo', 1),
                         status_msgs['SUCCESS_250'] %'DELE')
        res = self.execute('DELE bar', 1).split()[0]
        self.assertEqual(res, '550')
        self.assertEqual(self.execute('DELE', 1),
                         status_msgs['ERR_ARGS'])


    def testHELP(self):
        result = status_msgs['HELP_START'] #+ '\r\n'
        #result += 'Help goes here somewhen.\r\n'
        #result += status_msgs['HELP_END']

        self.assertEqual(self.execute('HELP', 1), result)


    # XXX: Test disabled due to ftplib error.
    def XXXtestLIST(self):
        conn = ftplib.FTP()
        try:
            conn.connect(LOCALHOST, self.port)
            conn.login('foo', 'bar')
            self.assertRaises(ftplib.Error, retrlines, conn, 'LIST /foo')
            listing = retrlines(conn, 'LIST')
            self.assert_(len(listing) > 0)
        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()


    def testNOOP(self):
        self.assertEqual(self.execute('NOOP', 0),
                         status_msgs['SUCCESS_200'] %'NOOP')
        self.assertEqual(self.execute('NOOP', 1),
                         status_msgs['SUCCESS_200'] %'NOOP')


    def testPASS(self):
        self.assertEqual(self.execute('PASS', 0),
                         status_msgs['LOGIN_MISMATCH'])
        self.assertEqual(self.execute(('USER blah', 'PASS bar'), 0),
                         status_msgs['LOGIN_MISMATCH'])


    def testQUIT(self):
        self.assertEqual(self.execute('QUIT', 0),
                         status_msgs['GOODBYE'])
        self.assertEqual(self.execute('QUIT', 1),
                         status_msgs['GOODBYE'])


    def testSTOR(self):
        conn = ftplib.FTP()
        try:
            conn.connect(LOCALHOST, self.port)
            conn.login('foo', 'bar')
            fp = StringIO('Speak softly')
            # Can't overwrite directory
            self.assertRaises(
                ftplib.error_perm, conn.storbinary, 'STOR /test', fp)
            fp = StringIO('Charity never faileth')
            # Successful write
            conn.storbinary('STOR /stuff', fp)
        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()


    def testUSER(self):
        self.assertEqual(self.execute('USER foo', 0),
                         status_msgs['PASS_REQUIRED'])
        self.assertEqual(self.execute('USER', 0),
                         status_msgs['ERR_ARGS'])



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Tests)

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
