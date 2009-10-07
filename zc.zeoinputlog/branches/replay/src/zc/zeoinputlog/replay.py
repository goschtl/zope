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
import logging
import marshal
import os
import sys
import threading
import time
import traceback
import transaction
import zc.ngi.async
import zc.ngi.adapters
import ZEO.ClientStorage
import ZODB.blob
import ZODB.FileStorage
import ZODB.POSException
import ZODB.TimeStamp
import ZODB.utils

logging.basicConfig()

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
            if not name.endswith(ZODB.blob.BLOB_SUFFIX):
                continue
            serial = name[:-len(ZODB.blob.BLOB_SUFFIX)]
            serial = ZODB.utils.repr_to_oid(serial)
            if serial >= tid:
                #print 'remove', base, name
                ZODB.blob.remove_committed(os.path.join(base, name))

def lastfs(fs):
    f = open(fs, 'rb')
    f.seek(-8, 2)
    f.seek(-8-ZODB.utils.u64(f.read(8)), 2)
    tid = f.read(8)
    return str(ZODB.TimeStamp.TimeStamp(tid))

def extract(fsname, log, outname):
    start = time_stamp(log.start())
    end = time_stamp(log.end())
    out = open(outname, 'wb')
    for t in ZODB.FileStorage.FileIterator(fsname, start, end):
        marshal.dump(
            ('t', t.tid, t.status, t.user, t.description, t.extension),
            out)
        for r in t:
            marshal.dump(('r', r.oid, r.tid, r.data), out)
        marshal.dump(('c',), out)
    out.close()

def mergelogs(l1, l2, out):
    files = open(l1, 'rb'), open(l2, 'rb')
    records = [marshal.load(f) for f in files]
    counts = [0, 0]
    fo = open(out, 'wb')
    while 1:
        if records[0][1] <= records[1][1]:
            index = 0
        else:
            index = 1
        session, timetime, message = records[index]
        marshal.dump(('%d%s' % (index, session), timetime, message), fo)
        try:
            records[index] = marshal.load(files[index])
        except EOFError:
            break

    index = not index
    while 1:
        session, timetime, message = records[index]
        marshal.dump(('%d%s' % (index, session), timetime, message), fo)
        try:
            records[index] = marshal.load(files[index])
        except EOFError:
            break

class Log(object):

    def __init__(self, fname):
        self.fname = fname

    def start(self):
        return iter(self).next()[1]

    _end = None
    def end(self):
        if self._end is not None:
            return self._end

        end = None
        for x in self:
            end = x[1]

        self._end = end
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

    def __len__(self):
        n = 0
        for x in self:
            n += 1
        return n

    def sessions(self):
        sessions = {}
        for session, timetime, msgid, async, op, args in self:
            stats = sessions.get(session)
            if stats is None:
                stats = sessions[session] = dict(
                    start_timetime=timetime,
                    ops={},
                    size=0,
                    )
            stats['end_timetime'] = timetime
            stats['ops'][op] = stats['ops'].get(op, 0) + 1
            stats['size'] += 1

        return sessions

    def splitsessions(self, sessions, outname):
        # Split the given sessions my splitting roughly half the calls
        # calls into a new session containing only loadEx calls
        sessions = set("0%s" % session for session in sessions)
        sizes = {}
        out = open(outname, 'wb')
        for session, timetime, msgid, async, op, args in self:
            session = "0%s" % session
            if (session in sessions
                and op == 'loadEx'
                and sizes.get(session, 0) > sizes.get('1'+session[1:], 0)
                ):
                session = '1'+session[1:]
            sizes[session] = sizes.get(session, 0) + 1
            marshal.dump(
                (session, timetime, cPickle.dumps((msgid, async, op, args), 1)
                 ),
                out)

    def splitsendblobs(self, sessions, outname):
        # Split the given sessions my splitting roughly half the
        # sendBlob calls calls into a new session.
        sessions = set("0%s" % session for session in sessions)
        sizes = {}
        out = open(outname, 'wb')
        for session, timetime, msgid, async, op, args in self:
            session = "0%s" % session
            if session in sessions and op == 'sendBlob':
                if sizes.get(session, 0) > sizes.get('1'+session[1:], 0):
                    session = '1'+session[1:]
                sizes[session] = sizes.get(session, 0) + 1
            marshal.dump(
                (session, timetime, cPickle.dumps((msgid, async, op, args), 1)
                 ),
                out)

class Transactions(object):


    def __init__(self, fname):
        self.fname = fname

    def __iter__(self):
        f = open(self.fname)
        while 1:
            try:
                yield Transaction(f, *marshal.load(f))
            except EOFError:
                break


class Transaction:

    def __init__(self, f, type_, tid, status, user, description, extension):
        assert type_ == 't'
        self.f = f
        self.id = tid
        self.status = status
        self.user = user
        self.description = description
        self._extension = extension

    used = False
    def __iter__(self):
        if self.used:
            return
        self.used = True
        while 1:
            data = marshal.load(self.f)
            if data[0] == 'c':
                break
            yield data[1:]

class Handler:

    msgid = 0
    closed = 0
    queueing = True

    def __init__(self, addr, session=None, handlers=None):
        if handlers is None:
            handlers = Handlers()
        self.handlers = handlers
        self.session = session
        self.addr = addr
        self.event = threading.Event()
        self.queue = []
        self.messages = {}
        self.times = handlers.times
        self.errtimes = handlers.errtimes
        self.lock = threading.Lock()
        zc.ngi.async.connect(addr, self)

    def connected(self, connection):
        self.handlers.connected += 1
        self.protocol = None
        self.connection = zc.ngi.adapters.Sized(connection)
        self.connection.setHandler(self)

    def failed_connect(self, reason):
        print time.ctime(), self.session, 'WTF failed connect', reason

    def handle_close(self, connection, reason):
        with self.lock:
            self.queueing = True

        self.connection = None
        print time.ctime(), self.session, 'WTF Closed', reason
        messages = sorted((v[2], v[0], v[1]) for v in self.messages.values())
        print time.ctime(), self.session, [v[:2] for v in messages]
        redo = [(0, v[1], v[2]) for v in messages
                if v[1] in ('sendBlob', 'loadEx')]
        self.queue.extend(redo)
        self.handlers.abandoned += len(messages) - len(redo)
        self.messages.clear()
        zc.ngi.async.connect(self.addr, self)
        self.handlers.connected -= 1

    def stop_queueing(self):
        assert self.queueing
        with self.lock:
            self.queueing = False
            self._process()

    def handle_input(self, connection, message):
        if self.protocol is None:
            self.protocol = message
            connection.write(self.protocol) # Echo it back
            self.queue.insert(0, (0, 'register', ('1', 0)))
            self.stop_queueing()
            self.event.set()
            return

        self.handlers.inputs += 1

        try:
            msgid, flags, op, args = cPickle.loads(message)
        except:
            print time.ctime(), self.session, 'bad message', repr(message)
            traceback.print_exception(*sys.exc_info())
            return

        #print '  got', self.session, msgid, flags, op
        if (op == '.reply'):
            ret = args
            op, args, start = self.messages.pop(msgid)
            elapsed = time.time()-start
            #print '    reply', op, [
            #    (v[0], v[2]) for v in self.messages.values()
            #    ], elapsed
            self.handlers.replies += 1
            if (isinstance(ret, tuple)
                and len(ret) == 2
                and isinstance(ret[1], Exception)
                ):
                n, t = self.errtimes.get(op, zz)
                self.errtimes[op] = n+1, t+elapsed
                print '  OOPS', op, args, elapsed, ret[0].__name__, ret[1]
                self.handlers.errors += 1
            else:
                n, t = self.times.get(op, zz)
                self.times[op] = n+1, t+elapsed

            self.stop_queueing()

    def call(self, async, op, args):
        self.queue.append((async, op, args))
        if op == 'vote':
            self.queue.append((0, 'tpc_abort', args))

        with self.lock:
            self._process()

    def _process(self):
        while self.queue and not self.queueing:
            async, op, args = self.queue.pop(0)

            self.msgid += 1

            #print '  call', self.session, self.msgid, async, op
            if not async:
                #print '    prev out', self.session, [
                #    (v[0], v[2]) for v in self.messages.values()]
                self.messages[self.msgid] = op, args, time.time()
                self.queueing = True

            self.connection.write(cPickle.dumps((self.msgid, async, op, args)))

zz = 0, 0

class Handlers:

    connected = async = calls = inputs = replies = errors = pending = 0
    abandoned = 0

    def __init__(self):
        self.errtimes = {}
        self.times = {}

def parse_addr(addr):
    addr = addr.split(':')
    return addr[0], int(addr[1])

def print_times(last_times, times, label):
    print 'Time per op (milliseconds)', label
    times = times.copy()
    for op in sorted(times):
        n, t = times[op]
        last = last_times.get(op)
        if last:
            n -= last[0]
            t -= last[1]
        print "%20s %10d %10.3f" % (op, n, t*1000/n)
    return times

def main(args=None):
    """Usage: script address log source

    Where:

       address
          The address of the zeo server to provide input to.

       log
          zeo input log

       source

          A marshalled extract of file-storage records for the period of the
          input log.

    """
    if args is None:
        args = sys.argv[1:]

    [addr, log, source] = args
    addr = parse_addr(addr)

    log = Log(log)

    handlers = Handlers()

    # Set up the client connections
    sessions = {}
    nhandlers = 0
    for session, timetime, msgid, async, op, args in log:
        if session not in sessions:
            handler = Handler(addr, nhandlers, handlers)
            sessions[session] = handler
            nhandlers += 1

    for handler in sessions.values():
        handler.event.wait(10)
        if not handler.event.is_set():
            raise ValueError("Couldn't connect.")

    # Now, we're ready to replay.

    cs = ZEO.ClientStorage.ClientStorage(addr)
    logiter = iter(log)
    logrecord = logiter.next()
    nt = nr = ni = 0
    start = lastnow = time.time()
    firsttt = lasttt = log.start()
    work = lastwork = 0
    speed = speed1 = None
    last_times = {}
    for t in Transactions(source):

        if nt and (nt%1000 == 0):
            last_times = print_times(last_times, handlers.times,
                                     "after %s transactions" % nt)

        sys.stdout.flush()
        pending = handlers.calls - handlers.replies - handlers.abandoned
        while pending > 10000:
            time.sleep(.01)
            pending = handlers.calls - handlers.replies - handlers.abandoned

        nt += 1

        tt = ZODB.TimeStamp.TimeStamp(t.id).timeTime()
        now = time.time()
        if now > start:
            speed = (tt-firsttt) / (now-start)
        if now > lastnow:
            speed1 = (tt-lasttt) / (now-lastnow)
        lastnow = now
        lasttt = tt
        work = nt + nr + handlers.calls + handlers.async
        print '=== top', time.ctime(), ZODB.TimeStamp.TimeStamp(time_stamp(tt))
        print '       ', handlers.connected, handlers.calls, handlers.replies,
        print handlers.errors, handlers.async, pending, speed, speed1
        while logrecord[1] < tt:
            ni += 1
            session, _, _, async, op, args = logrecord
            logrecord = logiter.next()
            if op in ('getAuthProtocol', 'register', 'tpc_finish'):
                continue
            sessions[session].call(async, op, args)
            if async:
                handlers.async += 1
            else:
                handlers.calls += 1
            #print op, args
            if op == 'vote':
                handlers.async += 1

        #print '=== begin'
        cs.tpc_begin(t, t.id, t.status)
        for oid, serial, data in t:
            if not data:
                continue
            nr += 1
            cs.restore(oid, serial, data, '', None, t)
        #print '=== vote'
        cs.tpc_vote(t)
        #print '=== finish'
        cs.tpc_finish(t)

    print '='*70

    print speed, nt, nt*3+nr, ni

    for op in sorted(handlers.errtimes):
        n, t = handlers.times[op]
        print 'err', op, n, t/n

    print_times(last_times, handlers.times,
                "after %s transactions" % nt)

    print_times({}, handlers.times, "overall")

