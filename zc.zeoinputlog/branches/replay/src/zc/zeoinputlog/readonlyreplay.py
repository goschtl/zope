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
"Replay ZEO input logs in read-only mode"

import cPickle
import logging
import marshal
import multiprocessing
import optparse
import os
import Queue
import sys
import tempfile
import threading
import time
import traceback
import transaction
import urllib2
import urlparse
import zc.ngi.adapters
import zc.ngi.async
import ZODB.TimeStamp
import ZODB.blob
import ZODB.utils

sys.setcheckinterval(999)

logging.basicConfig()

def time_stamp(timetime):
    return repr(ZODB.TimeStamp.TimeStamp(
        *time.gmtime(timetime)[:5]
        +(time.gmtime(timetime)[5]+divmod(timetime,1)[1],)
        ))

class Log(object):

    def __init__(self, fname, ops=None):
        self.fname = fname
        self.ops = ops

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
        ops = self.ops
        while 1:
            try:
                session, timetime, message = marshal.load(f)
            except EOFError:
                break

            msgid, async, op, args = cPickle.loads(message)
            if ops and op not in ops:
                continue

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

def zmqProcessFactory(zmqaddr):
    return (lambda target, args:
            multiprocessing.Process(
                target=zmqWorker, args = (zmqaddr, target, args))
            )

def zmqWorker(zmqaddr, target, args):
    import zmq
    context = zmq.Context()
    socket = context.socket(zmq.XREQ)
    socket.connect(zmqaddr)

    session = args[-3]
    socket.send(cPickle.dumps(session, 1))

    queue = zmqQueue(socket)

    target(*(args[:-2]+(queue, queue)))

class zmqQueue:

    def __init__(self, socket):
        self.socket = socket
        self._send = socket.send

    def get(self, block=True, timeout=None):
        return cPickle.loads(self.socket.recv(timeout*1000))

    def put(self, data):
        self._send(cPickle.dumps(data, 1))

class zmqBoss:

    def __init__(self, zmqaddr, sessions, handlers_queue, event):
        thread = threading.Thread(
            target = self.run,
            args = (zmqaddr, sessions, handlers_queue, event),
            )
        thread.daemon = True
        thread.start()

    def session_put(self, queue, addr):

        def put(ob):
            queue.put((addr, ob))

        return put

    def run(self, zmqaddr, sessions, handlers_queue, event):
        import zmq
        context = zmq.Context()
        socket = context.socket(zmq.XREP)
        socket.bind(zmqaddr)
        time.sleep(10) # Give lots of time to hook up w workers
        poller = self.poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        session_addrs = {}
        handler_queue = Queue.Queue()
        while 1:
            ready = dict(poller.poll(2000))
            if ready.get(socket) == zmq.POLLIN:
                addr, session = socket.recv_multipart()
                session = cPickle.loads(session)
                if isinstance(session, int):
                    session_addrs[session] = addr
                    sessions[session] = self.session_put(handler_queue, addr)
                else:
                    handlers_queue.put(session)
            else:
                break

        event.set()
        print 'Got', len(sessions), 'zmq workers'
        while 1:
            try:
                addr, ob = handler_queue.get(False)
            except Queue.Empty:
                pass
            else:
                socket.send_multipart([addr, cPickle.dumps(ob, 1)])
                continue

            ready = dict(poller.poll(10))
            if ready.get(socket) == zmq.POLLIN:
                _, data = socket.recv_multipart()
                data = cPickle.loads(data)
                if isinstance(data, int):
                    print 'Late session', data
                else:
                    handlers_queue.put(data)


class Handler:

    msgid = 0
    closed = 0
    queueing = True
    protocol = message = None

    def __init__(self, addr, session, inq, outq):
        self.session = session
        self.addr = addr
        def output(op, *args):
            outq.put((op, args))
        self.output = output
        self.condition = condition = threading.Condition()
        self.ngi = zc.ngi.async.Implementation()
        self.ngi.connect(addr, self)

        with condition:
            while 1:
                #print '__init__', self.protocol, self.message, inq.empty(),
                if self.protocol and not self.message:
                    try:
                        callargs = inq.get(True, 1.0)
                    except:
                        #print 'queue timeout'
                        continue
                    if callargs == 'stop':
                        connection = self.connection
                        if connection is not None:
                            connection.close()
                        return
                    async, op, args = callargs
                    assert not async
                    self.call(op, args)
                condition.wait(1)

    def call(self, op, args):
        assert not self.message
        self.msgid += 1
        #print time.ctime(), 'call', self.msgid, op, args
        self.message = [self.msgid, op, args]
        data = cPickle.dumps((self.msgid, 0, op, args))
        append = self.message.append

        @self.connection.writelines
        @apply
        def _():
            append(time.time())
            yield data

        self.output('request', op, args)

    def connected(self, connection):
        self.output('connect')
        self.protocol = None
        self.connection = zc.ngi.adapters.Sized(connection)
        self.connection.set_handler(self)

    def failed_connect(self, reason):
        print time.ctime(), self.session, 'WTF failed connect', reason

    def handle_close(self, connection, reason):
        with self.condition:
            self.protocol = self.message = None

        self.connection = None
        print time.ctime(), self.session, 'WTF Closed', reason
        self.output('disconnect', 0)
        self.ngi.connect(self.addr, self)

    def handle_input(self, connection, message):
        now = time.time()
        try:
            msgid, flags, op, args = cPickle.loads(message)
        except:
            if message[0] == 'Z':
                with self.condition:
                    if self.protocol is None:
                        connection.write(message) # Echo it back
                        self.call('register', ('1', 1))
                        self.protocol = message
                        self.condition.notifyAll()
                        return

            print time.ctime(), self.session, 'bad message', repr(message)
            traceback.print_exception(*sys.exc_info())
            return

        if op == 'invalidateTransaction':
            return
        #print time.ctime(), 'input', msgid, op
        if (op == '.reply'):
            ret = args
            with self.condition:
                rmsgid, op, args, start = self.message
                assert rmsgid == msgid
                elapsed = now-start
                #print elapsed * 1000
                self.message = None
                #print 'notift reply'
                self.condition.notifyAll()

            self.output('reply', op, args, ret, elapsed)


class S3Handler(Handler):

    def __init__(self, folder, addr, session, inq, outq):
        bucket_name, self.folder = folder.split('/', 1)
        import boto.s3.connection
        import boto.s3.key
        self.s3 = boto.s3.key.Key(
            boto.s3.connection.S3Connection().get_bucket(bucket_name))
        Handler.__init__(self, addr, session, inq, outq)

    def call(self, op, args):
        if op == 'sendBlob':
            oid, serial = args
            self.s3.key = "%s/%s/%s" % (
                self.folder, oid.encode('hex'), serial.encode('hex'))
            self.output('request', op, args)
            # f = tempfile.TemporaryFile()
            t = time.time()
            try:
                # self.s3.get_contents_to_file(f)
                self.s3.get_contents_as_string()
                ret = None
            except Exception, v:
                ret = None, v
            elapsed = time.time() - t
            self.output('reply', op, args, ret, elapsed)
            # f.close()

        else:
            Handler.call(self, op, args)



class HTTPHandler(Handler):

    def __init__(self, url, addr, session, inq, outq):
        if not url[-1] == '/':
            url += '/'
        self.blob_url = url
        self.blob_layout = ZODB.blob.BushyLayout()
        Handler.__init__(self, addr, session, inq, outq)

    def fetchblob(self, result, *args):
        ret = None
        try:
            path = self.blob_layout.getBlobFilePath(*args)
            for i in range(10):
                try:
                    r = urllib2.urlopen(self.blob_url+path, timeout=10)
                    r.read()
                    r.close()
                    break
                except urllib2.URLError, v:
                    if not 'timed out' in str(v):
                        raise
        except Exception, v:
            #traceback.print_exc()
            ret = None, Exception(str(v))
        except:
            ret = None, Exception('wtf')

        result.append(ret)

    def call(self, op, args):
        if op == 'sendBlob':
            self.output('request', op, args)
            t = time.time()
            r = []
            self.fetchblob(r, *args)
            if not r:
                print "WTF blob fetch %r" % (args,)
                ret = None, SystemError()
            else:
                ret = r[0]
            elapsed = time.time() - t

            self.output('reply', op, args, ret, elapsed)
        else:
            Handler.call(self, op, args)

zz = 0, 0

class Handlers:

    async = abandoned = active = 0

    def __init__(self, disconnected):
        self.times = {}
        self.disconnected = disconnected
        self.connected = self.maxactive = self.calls = self.replies = 0
        self.errors = 0
        self.event = threading.Event()

    def __repr__(self):
        return ("%(connected)s %(disconnected)s %(maxactive)s"
                " %(calls)s %(replies)s %(errors)s"
                % self.__dict__)

    def run(self, queue):
        while 1:
            got = queue.get()
            op, args = got
            getattr(self, op)(*args)

    def connect(self):
        self.disconnected -= 1
        if not self.disconnected:
            self.event.set()
        self.connected += 1

    def disconnect(self, abandoned):
        self.disconnected += 1
        self.connected -= 1
        self.abandoned += abandoned
        self.active -= abandoned

    def request(self, op, args):
        self.active += 1
        self.maxactive = max(self.maxactive, self.active)
        self.calls += 1

    def reply(self, op, args, ret, elapsed):
        self.active -= 1
        self.replies += 1
        if (isinstance(ret, tuple)
            and len(ret) == 2
            and isinstance(ret[1], Exception)
            ):
            op = op+'-error'
            self.errors += 1
        n, t = self.times.get(op, zz)
        self.times[op] = n+1, t+elapsed
        sys.stdout.flush()



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
        if n:
            print "%20s %10d %10.3f" % (op, n, t*1000/n)

    return times

parser = optparse.OptionParser("""
Usage:

    %prog [options] address log sessions

    %prog --zmq-boss tcp://IP:PORT [options] log

    %prog --zmq-workee tcp://IP:PORT [options] address sessions

    Where:

       address
          The address of the zeo server to provide input to.

       log
          zeo input log

       sessions
          A file containing a list of session identifiers.


    To use 0mq, start one or more worker processes and then start a
    boss porocess.  When specifying an IP, an IP #, rather than a host
    name must be used.

""")
parser.add_option("--max_records", "-m", dest='max_records',
                  type="int", default=999999999,
                  help="""
Maximum number of records to process.
""")
parser.add_option("--s3-folder", "-s", dest='s3',
                  help="""
Get blobs from the given s3 folder: BUCKET/FOLDER
""")
parser.add_option("--blob-url", "-u", dest='blob_url',
                  help="""
Get blobs from an HTTP server at the given URL.
""")
parser.add_option("--status-port", "-p", dest='status_port',
                  type="int",
                  help="Port to get status data from.")


parser.add_option("--zmq-boss");
parser.add_option("--zmq-worker");


def main(args=None):
    if args is None:
        args = sys.argv[1:]


    # Maybe add options for following:
    simulate_ssd = False

    print "$Id$"
    print args

    options, args = parser.parse_args(args)

    log = addr = sessionids = ()
    if options.zmq_boss:
        [addr, log] = args
    else:
        if options.zmq_worker:
            addr, sessionids = args
        else:
            addr, log, sessionids = args

    if log:
        log = Log(log, set(('loadEx', 'sendBlob')))
    if addr:
        addr = parse_addr(addr)
    if sessionids:
        sessionids = open(sessionids).read().strip().split()

    max_records = options.max_records


    # Set up the client connections
    sessions = {}
    handlers_queue = multiprocessing.Queue()
    processes = []

    if options.zmq_worker:
        process_factory = zmqProcessFactory(options.zmq_worker)
    else:
        process_factory = multiprocessing.Process

    for session in sessionids:
        session = int(session.strip())

        if session not in sessions:
            handler_queue = multiprocessing.Queue()
            if options.s3:
                process = process_factory(
                    target = S3Handler,
                    args = (options.s3,
                            addr, session, handler_queue, handlers_queue),
                    )
            elif options.blob_url:
                process = process_factory(
                    target = HTTPHandler,
                    args = (options.blob_url,
                            addr, session, handler_queue, handlers_queue),
                    )
            else:
                process = process_factory(
                    target = Handler,
                    args = (addr, session, handler_queue, handlers_queue),
                    )
            process.daemon = not options.zmq_worker
            process.start()
            processes.append(process)
            sessions[session] = handler_queue.put

    print len(sessionids), 'sessions'

    if options.zmq_worker:
        return

    if options.zmq_boss:
        handlers_queue = Queue.Queue()
        event = threading.Event()
        zmqBoss(options.zmq_boss, sessions, handlers_queue, event)
        event.wait()

    nsessions = len(sessions)
    handlers = Handlers(nsessions)
    thread = threading.Thread(target=handlers.run, args=(handlers_queue, ))
    thread.daemon = True
    thread.start()

    handlers.event.wait(10)
    if not handlers.event.is_set():
        raise ValueError("Couldn't connect.", handlers)

    # Now, we're ready to replay.
    nrecords = 0
    start = lastnow = time.time()
    firsttt = lasttt = log.start()
    speed = speed1 = None
    last_times = {}
    for session, timetime, msgid, async, op, args in log:

        if session not in sessions:     # Skip unknown sessions
            continue

        if simulate_ssd:
            if op == 'loadEx':
                args = (ZODB.utils.z64,)
            else:
                assert op in ('loadBefore', 'sendBlob')
                continue

        nwaaa = 0
        while nrecords-handlers.replies-handlers.errors > nsessions*3:
            if nwaaa and nwaaa%1000 == 0:
                print 'waiting', nrecords, handlers.replies, handlers.errors,
                print nrecords-handlers.replies-handlers.errors
                sys.stdout.flush()

            time.sleep(.01)
            nwaaa += 1

        if nrecords and (nrecords%10000 == 0):
            if (nrecords%100000 == 0):
                os.system("nc %s %s" % (addr[0], options.status_port))
                os.system("uptime")
                last_times = print_times(last_times, handlers.times,
                                         "after %s operations" % nrecords)
                print

            now = time.time()
            if now > start:
                speed = (timetime-firsttt) / (now-start)
            if now > lastnow:
                speed1 = (timetime-lasttt) / (now-lastnow)
            lastnow = now
            lasttt = timetime

            print nrecords,
            print time.strftime('%H:%M:%S', time.localtime(time.time())),
            print ZODB.TimeStamp.TimeStamp(time_stamp(timetime)), handlers,
            print speed, speed1, handlers.active, handlers_queue.qsize()

            sys.stdout.flush()


        nrecords += 1

        handlers.maxactive = 0

        sessions[session]((async, op, args))
        if nrecords >= max_records:
            break

    for put in sessions.values():
        put('stop')

    print '='*70

    print_times(last_times, handlers.times,
                "after %s transactions" % nrecords)

    print_times({}, handlers.times, "overall")
    sys.stdout.flush()

    for p in processes:
        p.join(1)

    sys.exit(0)
