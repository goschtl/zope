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

$Id: test_ftpserver.py,v 1.4 2003/02/03 15:09:01 jim Exp $
"""

import asyncore
import unittest
import tempfile
import os
import socket
import shutil
import sys
import traceback
from types import StringType
from StringIO import StringIO

from threading import Thread, Event
from zope.server.taskthreads import ThreadedTaskDispatcher
from zope.server.ftp.server import FTPServer, status_messages
from zope.server.adjustments import Adjustments
from zope.server.interfaces import ITask

from zope.server.ftp.tests import demofs

from zope.server.tests.asyncerror import AsyncoreErrorHook


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


class Tests(unittest.TestCase, AsyncoreErrorHook):

    def setUp(self):
        td.setThreadCount(1)
        self.orig_map_size = len(asyncore.socket_map)
        self.hook_asyncore_error()

        root_dir = demofs.Directory()
        root_dir['test'] = demofs.Directory()
        root_dir['test'].access['foo'] = 7
        root_dir['private'] = demofs.Directory()
        root_dir['private'].access['foo'] = 7
        root_dir['private'].access['anonymous'] = 0

        fs = demofs.DemoFileSystem(root_dir, 'foo')
        fs.writefile('/test/existing', StringIO('test initial data'))
        fs.writefile('/private/existing', StringIO('private initial data'))
        
        self.__fs = fs = demofs.DemoFileSystem(root_dir, 'root')
        fs.writefile('/existing', StringIO('root initial data'))

        fs_access = demofs.DemoFileSystemAccess(root_dir, {'foo': 'bar'})
        
        self.server = FTPServer(LOCALHOST, SERVER_PORT, fs_access,
                                task_dispatcher=td, adj=my_adj)
        if CONNECT_TO_PORT == 0:
            self.port = self.server.socket.getsockname()[1]
        else:
            self.port = CONNECT_TO_PORT
        self.run_loop = 1
        self.counter = 0
        self.thread_started = Event()
        self.thread = Thread(target=self.loop)
        self.thread.start()
        self.thread_started.wait(10.0)
        self.assert_(self.thread_started.isSet())

    def tearDown(self):
        self.run_loop = 0
        self.thread.join()
        td.shutdown()
        self.server.close()
        # Make sure all sockets get closed by asyncore normally.
        timeout = time() + 2
        while 1:
            if len(asyncore.socket_map) == self.orig_map_size:
                # Clean!
                break
            if time() >= timeout:
                self.fail('Leaked a socket: %s' % `asyncore.socket_map`)
                break
            asyncore.poll(0.1)

        self.unhook_asyncore_error()

    def loop(self):
        self.thread_started.set()
        import select
        from errno import EBADF
        while self.run_loop:
            self.counter = self.counter + 1
            # print 'loop', self.counter
            try:
                asyncore.poll(0.1)
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
                             status_messages['PASS_REQUIRED'] +'\r\n')
            ftp.send('PASS bar\r\n')
            self.assertEqual(ftp.recv(1024),
                             status_messages['LOGIN_SUCCESS'] +'\r\n')

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
                         status_messages['TRANSFER_ABORTED'])


    def testAPPE(self):
        conn = ftplib.FTP()
        try:
            conn.connect(LOCALHOST, self.port)
            conn.login('foo', 'bar')
            fp = StringIO('Charity never faileth')
            # Successful write
            conn.storbinary('APPE /test/existing', fp)
            self.assertEqual(self.__fs.files['test']['existing'].data,
                             'test initial dataCharity never faileth')
        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()

    def testAPPE_errors(self):
        conn = ftplib.FTP()
        try:
            conn.connect(LOCALHOST, self.port)
            conn.login('foo', 'bar')

            fp = StringIO('Speak softly')

            # Can't overwrite directory
            self.assertRaises(
                ftplib.error_perm, conn.storbinary, 'APPE /test', fp)

            # No such file
            self.assertRaises(
                ftplib.error_perm, conn.storbinary, 'APPE /nosush', fp)

            # No such dir
            self.assertRaises(
                ftplib.error_perm, conn.storbinary, 'APPE /nosush/f', fp)

            # Not allowed
            self.assertRaises(
                ftplib.error_perm, conn.storbinary, 'APPE /existing', fp)

        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()

    def testCDUP(self):
        self.assertEqual(self.execute(('CWD test', 'CDUP'), 1),
                         status_messages['SUCCESS_250'] %'CDUP')
        self.assertEqual(self.execute('CDUP', 1),
                         status_messages['SUCCESS_250'] %'CDUP')


    def testCWD(self):
        self.assertEqual(self.execute('CWD test', 1),
                         status_messages['SUCCESS_250'] %'CWD')
        self.assertEqual(self.execute('CWD foo', 1),
                         status_messages['ERR_NO_DIR'] %'/foo')


    def testDELE(self):
        self.assertEqual(self.execute('DELE test/existing', 1),
                         status_messages['SUCCESS_250'] %'DELE')
        res = self.execute('DELE bar', 1).split()[0]
        self.assertEqual(res, '550')
        self.assertEqual(self.execute('DELE', 1),
                         status_messages['ERR_ARGS'])


    def XXXtestHELP(self):
        # XXX This test doesn't work.  I think it is because execute()
        #     doesn't read the whole reply.  The execeute() helper
        #     function should be fixed, but that's for another day.
        result = status_messages['HELP_START'] + '\r\n'
        result += 'Help goes here somewhen.\r\n'
        result += status_messages['HELP_END']

        self.assertEqual(self.execute('HELP', 1), result)


    def testLIST(self):
        conn = ftplib.FTP()
        try:
            conn.connect(LOCALHOST, self.port)
            conn.login('anonymous', 'bar')
            self.assertRaises(ftplib.Error, retrlines, conn, 'LIST /foo')
            listing = retrlines(conn, 'LIST')
            self.assert_(len(listing) > 0)
            listing = retrlines(conn, 'LIST -la')
            self.assert_(len(listing) > 0)
        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()

    def testMKDLIST(self):
        self.execute(['MKD test/f1', 'MKD test/f2'], 1)
        conn = ftplib.FTP()
        try:
            conn.connect(LOCALHOST, self.port)
            conn.login('foo', 'bar')
            listing = []
            conn.retrlines('LIST /test', listing.append)
            self.assert_(len(listing) > 2)
            listing = []
            conn.retrlines('LIST -lad test/f1', listing.append)
            self.assertEqual(len(listing), 1)
            self.assertEqual(listing[0][0], 'd')
        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()


    def testNOOP(self):
        self.assertEqual(self.execute('NOOP', 0),
                         status_messages['SUCCESS_200'] %'NOOP')
        self.assertEqual(self.execute('NOOP', 1),
                         status_messages['SUCCESS_200'] %'NOOP')


    def testPASS(self):
        self.assertEqual(self.execute('PASS', 0),
                         status_messages['LOGIN_MISMATCH'])
        self.assertEqual(self.execute(('USER blah', 'PASS bar'), 0),
                         status_messages['LOGIN_MISMATCH'])


    def testQUIT(self):
        self.assertEqual(self.execute('QUIT', 0),
                         status_messages['GOODBYE'])
        self.assertEqual(self.execute('QUIT', 1),
                         status_messages['GOODBYE'])


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
            conn.storbinary('STOR /test/stuff', fp)
            self.assertEqual(self.__fs.files['test']['stuff'].data,
                             'Charity never faileth')
        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()


    def testSTOR_over(self):
        conn = ftplib.FTP()
        try:
            conn.connect(LOCALHOST, self.port)
            conn.login('foo', 'bar')
            fp = StringIO('Charity never faileth')
            conn.storbinary('STOR /test/existing', fp)
            self.assertEqual(self.__fs.files['test']['existing'].data,
                             'Charity never faileth')
        finally:
            conn.close()
        # Make sure no garbage was left behind.
        self.testNOOP()


    def testUSER(self):
        self.assertEqual(self.execute('USER foo', 0),
                         status_messages['PASS_REQUIRED'])
        self.assertEqual(self.execute('USER', 0),
                         status_messages['ERR_ARGS'])



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Tests)

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
