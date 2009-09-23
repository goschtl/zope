##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
"""Replay ZEO input logs

This is a bit tricky.  If we just play the log, the writes are likely
to be processed differently than they were before, because the server
will handle them in different orders.  This has lots of
implications. For example, a set of conflicting transactions may have
a different winner, leading to different objects being created.

We'll deal with this by aborting any writes in the input.  We'll still
process the writes, but we'll convert transaction_vote calls to
transaction_aborts.

We'll get actual input data by "recovering" data from a full data file.  We'll play back the input log only as
fast as we recover.  We won't send an input log message whos time is
>= the time of the last recovered transaction.

So, to replay, you'll need:

- an input log
- a test database
- a non-test source database

The test database is truncated to the beginning of the input log.

The reply script will iterate over the source database, starting at
the time if the first input log message.  As we recover, we'll also
send input messages.  We'll stop when we get to the end of the input
log.

We'll time 2-way calls.  We'll also time blob loads. Finally, we'll
time how long it takes to play the input log.


"""


import cPickle
import marshal
import os
import sys
import threading
import time
import zc.ngi.async
import zc.ngi.adapters
import ZODB.Blob
import ZODB.FileStorage
import ZODB.POSException
import ZODB.TimeStamp
import ZODB.utils


def time_stamp(timetime):
    return repr(ZODB.TimeStamp.TimeStamp(
        *time.gmtime(timetime)[:5]
        +(time.gmtime(timetime)[5]+divmod(timetime,1)[1],)
        ))

def truncatefs(t, fs, blobs=None):
    """Truncate a file storage to time (time.time) t.
    """
    tid = time_stamp(t)
    it = ZODB.FileStorage.FileIterator(fs, start=tid)
    open(fs, 'r+b').truncate(it._pos)
    if blobs is None:
        return
    for base, dirs, files in os.walk(blobs):
        for name in files:
            if not name.endswith(BLOB_SUFFIX):
                continue
            serial = filename[:-len(ZODB.Blob.BLOB_SUFFIX)]
            serial = ZODB.utils.repr_to_oid(serial)
            if serial >= tid:
                ZODB.Blob.remove_committed(os.path.join(base, name))


def extract(fsname, log, outname):
    start = time_stamp(log.start())
    end = time_stamp(log.end())
    out = open(outname, 'wb')
    for t in ZODB.FileStorage.FileIterator(fsname, start, end):
        marshal.dump(('t', t.tid, t.status, t.user, t.desc, t.extension),
                     out)
        for r in t:
            marshal.dump(('r', r.oid, r.tid, r.data), out)
        marshal.dump(('c',), out)
    out.close()

class Log(object):

    def __init__(self, fname):
        self.fname = fname

    def start(self):
        return iter(self).next()[1]

    def end(self):
        end = None
        for x in self:
            end = x[1]
        return end

    def __iter__(self):
        f = open(self.fname)
        while 1:
            try:
                session, timetime, message = marshal.load(f)
            except EOFError:
                break

            msgid, async, op, args = cPickle.loads(message)

            yield session, timetime, msgid, async, op, args

class Handler:

    protocol = None
    msgid = 0

    def __init__(self):
        self.event = threading.Event()
        self.queue = []
        self.message = {}
        self.errtimes = []
        self.times = []

    def connected(self, connection):
        self.connection = zc.ngi.adapters.Sized(connection)
        connection.set_handler(self)
        self.event.set()

    def failed_connect(self, reason):
        print 'WTF failed connect', reason

    def handle_close(self, reason):
        print 'WTF Closed', reason

    def handle_input(self, message):
        if self.protocol is None:
            self.protocol = message
            self.connection.write(self.protocol) # Echo it back
            self.call(0, 'register', ('1', 0))
            self.event.set()
            return

        now = time.time()
        msgid, flags, op, args = cPickle.loads(message)
        if (op == '.reply'):
            ret = args
            op, args, start, blob = self.messages.pop(msgid)
            if (isinstance(ret, tuple)
                and len(ret) == 2
                and isinstance(ret[1], Exception)
                ):
                err = ret[1]
                self.errtimes.append(now-start)
                if isinstance(err, ZODB.POSException.POSKeyError):
                    if op == 'sendBlob':
                        # Hm. May be due to a bad serial.
                        # queue a
                    self.queue.append((op, args))
                    return
                print 'OOPS', ret[0].__name__, ret[1]
                # Maybe we should retry messages that generate errors.
            else:
                self.times.append(now-start)
                if blob:
                    assert op == 'loadEx'
                    oid = args[0]
                    tid = ret[1]
                    self.queue.append('sendBlob', (oid, tid))
        else:
            if op == 'receiveBlobStop':
                key = args
                start = self.messages.pop(key)
                self.times.append(now-start)

    def call(self, async, op, args):
        self.msgid += 1
        if not async:
            self.messages[msgid] = op, args, time.time(), 0

        self.connection.write(cPickle.dumps((msgid, async, op, args)))

def parse_addr(addr):
    addr = addr.split(':')
    return addr[0], int(addr[1])

def main(args=None):
    """Usage: script address log source

    Where:

       address
          The address of the zeo server to provide input to.

       log
          zeo input log

       source

          A file-storage file that contains just the transaction
          corresponding to the input log

    """
    if args is None:
        args = sys.argv[1:]

    [addr, log, source] = args
    addr = parse_addr(addr)

    # Set up the client connections
    sessions = {}
    for session, timetime, msgid, async, op, args in Log(log):
        if session not in sessions:
            handler = Handler()
            sessions[session] = handler
            zc.ngi.async.connect(addr, handler)

    for handler in sessions.values():
        handler.event.wait(10)
        if not handler.event.is_set():
            raise ValueError("Couldn't connect.")

    # Now, we're ready to replay.
    for session, timetime, msgid, async, op, args in Log(log):
        if op in ('getAuthProtocol', 'register'):
            continue
        sessions[session].call(async, op, args)
