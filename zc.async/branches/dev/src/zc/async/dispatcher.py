import time
import datetime
import Queue
import thread
import threading

import twisted.python.failure
import twisted.internet.defer
import ZODB.POSException
import transaction
import transaction.interfaces
import zope.component
import zc.twist

import zc.async.utils
import zc.async.interfaces

def _get(reactor, job, name, default, timeout, poll, deferred, start=None):
    now = time.time()
    if start is None:
        start = now
    if name in job.annotations:
        res = job.annotations[name]
    elif start + timeout < now:
        res = default
    else:
        partial = zc.twist.Partial(
            _get, reactor, job, name, default, timeout, poll, deferred,
            start)
        partial.setReactor(reactor)
        reactor.callLater(min(poll, start + timeout - now), partial)
        return
    deferred.setResult(res)

class Result(object):

    result = None

    def __init__(self):
        self._event = threading.Event()
    
    def setResult(self, value):
        self.result = value
        self._event.set()

    def wait(self, *args):
        self._event.wait(*args)

class Local(threading.local):

    job = None
    dispatcher = None

    def getJob(self):
        return self.job

    def getDispatcher(self):
        return self.dispatcher

    def getReactor(self):
        return self.dispatcher.reactor

    def setLiveAnnotation(self, name, value, job=None):
        if self.job is None or self.dispatcher.reactor is None:
            raise ValueError('not initialized')
        if job is None:
            job = self.job
        partial = zc.twist.Partial(
            job.annotations.__setitem__, name, value)
        partial.setReactor(self.dispatcher.reactor)
        self.dispatcher.reactor.callFromThread(partial)

    def getLiveAnnotation(self, name, default=None, timeout=0,
                          poll=1, job=None):
        if self.job is None or self.dispatcher.reactor is None:
            raise ValueError('not initialized')
        if job is None:
            job = self.job
        deferred = Result()
        partial = zc.twist.Partial(
            _get, self.dispatcher.reactor, job, name, default, timeout, poll,
            deferred)
        partial.setReactor(self.dispatcher.reactor)
        self.dispatcher.reactor.callFromThread(partial)
        deferred.wait(timeout+2)
        return deferred.result

local = Local()


class PollInfo(dict):
    key = None
    @property
    def utc_timestamp(self):
        if self.key is not None:
            return zc.async.utils.long_to_dt(self.key)


class AgentThreadPool(object):

    _size = 0

    def __init__(self, dispatcher, name, size):
        self.dispatcher = dispatcher
        self.name = name
        self.queue = Queue.Queue(0)
        self._threads = []
        self.setSize(size)

    def getSize(self):
        return self._size

    def perform_thread(self):
        local.dispatcher = self.dispatcher
        try:
            job = self.queue.get()
            while job is not None:
                db, identifier, info = job
                conn = db.open()
                try:
                    transaction.begin()
                    job = conn.get(identifier)
                    info['thread'] = thread.get_ident()
                    local.job = job
                    try:
                        job() # this does the committing and retrying, largely
                    except ZODB.POSException.TransactionError:
                        transaction.abort()
                        while 1:
                            try:
                                job.fail()
                                transaction.commit()
                            except ZODB.POSException.TransactionError:
                                transaction.abort() # retry forever (!)
                            else:
                                break
                finally:
                    local.job = None
                    transaction.abort()
                    conn.close()
                job = self.queue.get()
        finally:
            if self.dispatcher.activated:
                # this may cause some bouncing, but we don't ever want to end
                # up with fewer than needed.
                self.dispatcher.reactor.callFromThread(self.setSize)
    
    def setSize(self, size=None):
        # this should only be called from the thread in which the reactor runs
        # (otherwise it needs locks)
        old = self._size
        if size is None:
            size = old
        else:
            self._size = size
        res = []
        ct = 0
        for t in self._threads:
            if t.isAlive():
                res.append(t)
                ct += 1
        self._threads[:] = res
        if ct < size:
            for i in range(max(size - ct, 0)):
                t = threading.Thread(target=self.perform_thread)
                t.setDaemon(True)
                self._threads.append(t)
                t.start()
        elif ct > size:
            # this may cause some bouncing, but hopefully nothing too bad.
            for i in range(ct - size):
                self.queue.put(None)
        return size - old # size difference


class Dispatcher(object):

    activated = False

    def __init__(self, db, reactor, poll_interval=5, uuid=None):
        self.db = db
        self.reactor = reactor # we may allow the ``reactor`` argument to be
        # None at some point, to default to the installed Twisted reactor.
        self.poll_interval = poll_interval
        if uuid is None:
            uuid = zope.component.getUtility(zc.async.interfaces.IUUID)
        self.UUID = uuid
        self.polls = zc.async.utils.Periodic(
            period=datetime.timedelta(days=1), buckets=4)
        self._activated = set()
        self.queues = {}
        self.dead_pools = []

    def _getJob(self, agent):
        try:
            job = agent.claimJob()
        except zc.twist.EXPLOSIVE_ERRORS:
            transaction.abort()
            raise
        except:
            transaction.abort()
            zc.async.utils.log.error(
                'Error trying to get job for UUID %s from '
                'agent %s (oid %s) in queue %s (oid %s)', 
                self.UUID, agent.name, agent._p_oid,
                agent.queue.name,
                agent.queue._p_oid, exc_info=True)
            return zc.twist.sanitize(
                twisted.python.failure.Failure())
        res = self._commit(
            'Error trying to commit getting a job for UUID %s from '
            'agent %s (oid %s) in queue %s (oid %s)' % (
            self.UUID, agent.name, agent._p_oid,
            agent.queue.name,
            agent.queue._p_oid))
        if res is None:
            res = job
        return res

    def _commit(self, debug_string=''):
        retry = 0
        while 1:
            try:
                transaction.commit()
            except ZODB.POSException.TransactionError:
                transaction.abort()
                if retry >= 5:
                    zc.async.utils.log.error(
                        'Repeated transaction error trying to commit in '
                        'zc.async: %s', 
                        debug_string, exc_info=True)
                    return zc.twist.sanitize(
                        twisted.python.failure.Failure())
                retry += 1
            except zc.twist.EXPLOSIVE_ERRORS:
                transaction.abort()
                raise
            except:
                transaction.abort()
                zc.async.utils.log.error(
                    'Error trying to commit: %s', 
                    debug_string, exc_info=True)
                return zc.twist.sanitize(
                    twisted.python.failure.Failure())
            else:
                break

    def poll(self):
        conn = self.db.open()
        poll_info = PollInfo()
        try:
            queues = conn.root().get(zc.async.interfaces.KEY)
            if queues is None:
                transaction.abort()
                return
            for queue in queues.values():
                poll_info[queue.name] = None
                if self.UUID not in queue.dispatchers:
                    queue.dispatchers.register(self.UUID)
                da = queue.dispatchers[self.UUID]
                if queue._p_oid not in self._activated:
                    if da.activated:
                        if da.dead:
                            da.deactivate()
                        else:
                            zc.async.utils.log.error(
                                'UUID %s already activated in queue %s (oid %s): '
                                'another process?',
                                self.UUID, queue.name, queue._p_oid)
                            continue
                    da.activate()
                    self._activated.add(queue._p_oid)
                    # removed below if transaction fails
                    res = self._commit(
                        'Error trying to commit activation of UUID %s in '
                        'queue %s (oid %s)' % (
                            self.UUID, queue.name, queue._p_oid))
                    if res is not None:
                        self._activated.remove(queue._p_oid)
                        continue
                queue_info = poll_info[queue.name] = {}
                pools = self.queues.get(queue.name)
                if pools is None:
                    pools = self.queues[queue.name] = {}
                for name, agent in da.items():
                    job_info = []
                    agent_info = queue_info[name] = {
                        'size': None, 'len': None, 'error': None,
                        'new_jobs': job_info}
                    try:
                        agent_info['size'] = agent.size
                        agent_info['len'] = len(agent)
                    except zc.twist.EXPLOSIVE_ERRORS:
                        transaction.abort()
                        raise
                    except:
                        agent_info['error'] = zc.twist.sanitize(
                            twisted.python.failure.Failure())
                        transaction.abort()
                        continue
                    pool = pools.get(name)
                    if pool is None:
                        pool = pools[name] = AgentThreadPool(
                            self, name, agent_info['size'])
                        conn_delta = agent_info['size']
                    else:
                        conn_delta = pool.setSize(agent_info['size'])
                    if conn_delta:
                        db = queues._p_jar.db()
                        db.setPoolSize(db.getPoolSize() + conn_delta)
                    job = self._getJob(agent)
                    while job is not None:
                        if isinstance(job, twisted.python.failure.Failure):
                            agent_info['error'] = job
                            job = None
                            try:
                                agent.failure = res
                            except zc.twist.EXPLOSIVE_ERRORS:
                                transaction.abort()
                                raise
                            except:
                                transaction.abort()
                                zc.async.utils.log.error(
                                    'error trying to stash failure on agent')
                            else:
                                # TODO improve msg
                                self._commit('trying to stash failure on agent')
                        else:
                            info = {'oid': job._p_oid,
                                    'callable': repr(job.callable),
                                    'begin_after': job.begin_after.isoformat(),
                                    'quota_names': job.quota_names,
                                    'assignerUUID': job.assignerUUID,
                                    'thread': None}
                            job_info.append(info)
                            pool.queue.put(
                                (job._p_jar.db(), job._p_oid, info))
                            job = self._getJob(agent)
                queue.dispatchers.ping(self.UUID)
                self._commit('trying to commit ping')
                if len(pools) > len(queue_info):
                    conn_delta = 0
                    for name, pool in pools.items():
                        if name not in agent_info:
                            conn_delta += pool.setSize(0)
                            self.dead_pools.append(pools.pop(name))
                    if conn_delta:
                        db = queues._p_jar.db()
                        # this is a bit premature--it should really happen
                        # when all threads are complete--but since the pool just
                        # complains if the size is not honored, and this approach
                        # is easier, we're doing this.
                        db.setPoolSize(db.getPoolSize() + conn_delta)
            if len(self.queues) > len(poll_info):
                conn_delta = 0
                for queue_pools in self.queues.values():
                    if name not in poll_info:
                        for name, pool in queue_pools.items():
                            conn_delta += pool.setSize(0)
                            self.dead_pools.append(queue_pools.pop(name))
                if conn_delta:
                    # this is a bit premature--it should really happen
                    # when all threads are complete--but since the pool just
                    # complains if the size is not honored, and this approach
                    # is easier, we're doing this.
                    self.db.setPoolSize(self.db.getPoolSize() + conn_delta)
        finally:
            transaction.abort()
            conn.close()
            self.polls.add(poll_info)

    def directPoll(self):
        if not self.activated:
            return
        try:
            self.poll()
        finally:
            self.reactor.callLater(self.poll_interval, self.directPoll)

    def _inThreadPoll(self, deferred):
        try:
            self.poll()
        finally:
            self.reactor.callFromThread(deferred.callback, None)

    def threadedPoll(self):
        if not self.activated:
            return
        deferred = twisted.internet.defer.Deferred()
        self.reactor.callInThread(self._inThreadPoll, deferred)
        deferred.addCallback(
            lambda result: self.reactor.callLater(
                self.poll_interval, self.threadedPoll))

    def activate(self, threaded=False):
        if self.activated:
            raise ValueError('already activated')
        self.activated = True
        self.db.setPoolSize(self.db.getPoolSize() + 1)
        if threaded:
            self.reactor.callWhenRunning(self.threadedPoll)
        else:
            self.reactor.callWhenRunning(self.directPoll)
        self.reactor.addSystemEventTrigger(
            'before', 'shutdown', self.deactivate)

    def deactivate(self):
        if not self.activated:
            raise ValueError('not activated')
        self.activated = False
        conn = self.db.open()
        try:
            queues = conn.root().get(zc.async.interfaces.KEY)
            if queues is not None:
                for queue in queues.values():
                    da = queue.dispatchers.get(self.UUID)
                    if da is not None and da.activated:
                        da.deactivate()
                self._commit('trying to tear down')
        finally:
            transaction.abort()
            conn.close()
        conn_delta = 0
        for queue_pools in self.queues.values():
            for name, pool in queue_pools.items():
                conn_delta += pool.setSize(0)
                self.dead_pools.append(queue_pools.pop(name))
        conn_delta -= 1
        self.db.setPoolSize(self.db.getPoolSize() + conn_delta)
