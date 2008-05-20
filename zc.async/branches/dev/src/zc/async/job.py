##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
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
import time
import types
import datetime
import logging

import BTrees.OOBTree
import ZODB.POSException
import ZEO.Exceptions
import transaction.interfaces
import persistent
import persistent.list
import persistent.mapping
import twisted.internet.defer
import twisted.python.failure
import zope.interface
import zc.queue
import zc.twist
import rwproperty
import pytz

import zc.async.interfaces
import zc.async.utils

def _repr(obj):
    if isinstance(obj, persistent.Persistent):
        dbname = "?"
        if obj._p_jar is not None:
            dbname = getattr(obj._p_jar.db(), 'database_name', "?")
            if dbname != '?':
                dbname = repr(dbname)
        if obj._p_oid is not None:
            oid = ZODB.utils.u64(obj._p_oid)
        else:
            oid = '?'
        return '%s.%s (oid %s, db %s)' % (
            obj.__class__.__module__,
            obj.__class__.__name__,
            oid,
            dbname)
    elif isinstance(obj, types.FunctionType):
        return '%s.%s' % (obj.__module__, obj.__name__)
    else:
        return repr(obj)

def success_or_failure(success, failure, res):
    callable = None
    if isinstance(res, twisted.python.failure.Failure):
        if failure is not None:
            callable = failure
    elif success is not None:
        callable = success
    if callable is None:
        return res
    return callable(res)

def completeStartedJobArguments(job, result):
    if isinstance(result, twisted.python.failure.Failure):
        for collection in (job.args, job.kwargs.values()):
            for a in collection:
                if zc.async.interfaces.IJob.providedBy(a):
                    status = a.status
                    if status == zc.async.interfaces.ACTIVE:
                        a.fail()
                    elif status == zc.async.interfaces.CALLBACKS:
                        a.resumeCallbacks()

class IRetries(zope.interface.Interface): # XXX move
    def jobError(failure, data_cache):
        """whether and how to retry after an error while performing job.
        
        return boolean as to whether to retry, or a datetime or timedelta to
        reschedule the job in the queue.  An empty timedelta means to rescedule
        for immediately, before any pending calls in the queue."""

    def transactionError(failure, data_cache):
        """whether to retry after trying to commit a job's successful result.
        
        return boolean as to whether to retry, or a datetime or timedelta to
        reschedule the job in the queue.  An empty timedelta means to rescedule
        for immediately, before any pending calls in the queue."""

    def interrupted():
        """whether to retry after a dispatcher dies when job was in progress.
        
        return boolean as to whether to retry, or a datetime or timedelta to
        reschedule the job in the queue.  An empty timedelta means to rescedule
        for immediately, before any pending calls in the queue."""

    def updateData(data_cache):
        """right before committing a job, retry is given a chance to stash
        information it has saved in the data_cache."""

class Retries(persistent.Persistent): # default for '' IRetries
    zope.component.adapts(zc.async.interfaces.IJob)
    zope.interface.implements(zc.async.interfaces.IRetries)

    # exceptions, data_cache key, max retry, initial backoff seconds,
    # incremental backoff seconds, max backoff seconds
    internal_exceptions = (
        ((ZEO.Exceptions.ClientDisconnected,), 'zeo_disconnected',
         None, 5, 5, 60),
        ((ZODB.POSException.TransactionError,), 'transaction_error',
         5, 0, 0, 0),
    )
    transaction_exceptions = internal_exceptions
    max_interruptions = 10

    def __init__(self, job):
        self.parent = self.__parent__ = job
        self.data = BTrees.family32.OO.BTree()

    def updateData(data_cache):
        if 'first_active' in self.data and 'first_active' in data_cache:
            data_cache.pop('first_active')
        self.data.update(data_cache)

    def jobError(self, failure, data_cache):
        return self._process(failure, data_cache, self.internal_exceptions)

    def transactionError(self, failure, data_cache):
        return self._process(failure, data_cache, self.transaction_exceptions)

    def _process(self, failure, data_cache, exceptions):
        for (exc, key, max_count, init_backoff,
             incr_backoff, max_backoff) in exceptions:
            if failure.check(*exc) is not None:
                count = data_cache.get(key, 0) + 1
                if max_count is not None and count >= max_count:
                    return False
                backoff = min(max_backoff,
                              (init_backoff + (count-1) * incr_backoff))
                if backoff:
                    time.sleep(backoff)
                data_cache[key] = count
                data_cache['last_' + key] = failure
                if 'first_active' not in data_cache:
                    data_cache['first_active'] = self.parent.active_start
                return True
        return False

    def interrupted(self):
        if 'first_active' not in self.data:
            self.data['first_active'] = self.parent.active_start
        ct = self.data['interruptions'] = self.data.get('interruptions', 0) + 1
        return self.max_interruptions is None or ct <= self.max_interruptions

class RetrySystemErrorsForever(Retries): # default for 'callback' IRetries
    # retry on ZEO failures and Transaction errors during the job forever
    # retry on transactionErrors and interrupteds forever.
    internal_exceptions = (
        ((ZEO.Exceptions.ClientDisconnected,), 'zeo_disconnected',
         None, 5, 5, 60),
        ((ZODB.POSException.TransactionError,), 'transaction_error',
         None, 0, 0, 0),
    )
    
    max_interruptions = None

    def transactionError(self, failure, data_cache):
        res = super(RetryForever, self).transactionError(failure, data_cache)
        if not res:
            # that just means we didn't record it.  We actually are going to
            # retry.
            key = 'other'
            data_cache['other'] = data_cache.get('other', 0) + 1
            data_cache['last_other'] = failure
            if 'first_active' not in data_cache:
                data_cache['first_active'] = self.parent.active_start
        return True # always retry

class Job(zc.async.utils.Base):

    zope.interface.implements(zc.async.interfaces.IJob)

    _callable_root = _callable_name = _result = None
    _status = zc.async.interfaces.NEW
    _begin_after = _begin_by = _active_start = _active_end = None
    key = None
    # default_retry_policy and retry_policy should either be name to adapt job
    # to IRetries, or factory, or None.
    default_retry_policy = ''
    retry_policy = None
    retries = None
    default_error_log_level = logging.ERROR
    error_log_level = None

    @property
    def effective_error_log_level(self):
        if self.error_log_level is None:
            return self.default_error_log_level
        return self.error_log_level

    @property
    def effective_retry_policy(self):
        if self.retry_policy is None:
            return self.default_retry_policy
        return self.retry_policy

    assignerUUID = None
    _quota_names = ()

    def __init__(self, *args, **kwargs):
        self.args = persistent.list.PersistentList(args) # TODO: blist
        self.callable = self.args.pop(0)
        self.kwargs = persistent.mapping.PersistentMapping(kwargs)
        self.callbacks = zc.queue.PersistentQueue()
        self.annotations = BTrees.OOBTree.OOBTree()

    @property
    def active_start(self):
        return self._active_start

    @property
    def active_end(self):
        return self._active_end

    @property
    def initial_callbacks_end(self):
        return self.key and zc.async.utils.long_to_dt(self.key).replace(
            tzinfo=pytz.UTC)

    @property
    def quota_names(self):
        return self._quota_names
    @rwproperty.setproperty
    def quota_names(self, value):
        if isinstance(value, basestring):
            raise TypeError('provide an iterable of names')
        status = self.status
        if status != zc.async.interfaces.NEW:
            if status == zc.async.interfaces.PENDING:
                quotas = self.queue.quotas
                for name in value:
                    if name not in quotas:
                        raise ValueError('unknown quota name', name)
            else:
                raise zc.async.interfaces.BadStatusError(
                    'can only set quota_names when a job has NEW or PENDING '
                    'status')
        self._quota_names = tuple(value)

    @property
    def begin_after(self):
        return self._begin_after
    @rwproperty.setproperty
    def begin_after(self, value):
        if self.status != zc.async.interfaces.NEW:
            raise zc.async.interfaces.BadStatusError(
                'can only set begin_after when a job has NEW status')
        if value is not None:
            if value.tzinfo is None:
                raise ValueError('cannot use timezone-naive values')
            else:
                value = value.astimezone(pytz.UTC)
        self._begin_after = value

    @property
    def begin_by(self):
        return self._begin_by
    @rwproperty.setproperty
    def begin_by(self, value):
        if self.status not in (zc.async.interfaces.PENDING,
                               zc.async.interfaces.NEW):
            raise zc.async.interfaces.BadStatusError(
                'can only set begin_by when a job has NEW or PENDING status')
        if value is not None:
            if value < datetime.timedelta():
                raise ValueError('negative values are not allowed')
        self._begin_by = value

    @property
    def queue(self):
        ob = self.parent
        while (ob is not None and
               (zc.async.interfaces.IJob.providedBy(ob) or
                zc.async.interfaces.IAgent.providedBy(ob) or
                zc.async.interfaces.IDispatcherAgents.providedBy(ob))):
            ob = ob.parent
        if not zc.async.interfaces.IQueue.providedBy(ob):
            ob = None
        return ob

    @property
    def agent(self):
        ob = self.parent
        while (ob is not None and
               zc.async.interfaces.IJob.providedBy(ob)):
            ob = ob.parent
        if not zc.async.interfaces.IAgent.providedBy(ob):
            ob = None
        return ob

    @property
    def result(self):
        return self._result

    @property
    def status(self):
        # NEW -> (PENDING -> ASSIGNED ->) ACTIVE -> CALLBACKS -> COMPLETED
        if self._status == zc.async.interfaces.NEW:
            ob = self.parent
            while (ob is not None and
                   zc.async.interfaces.IJob.providedBy(ob)):
                ob = ob.parent
            if zc.async.interfaces.IAgent.providedBy(ob):
                return zc.async.interfaces.ASSIGNED
            elif zc.async.interfaces.IQueue.providedBy(ob):
                return zc.async.interfaces.PENDING
        return self._status

    @classmethod
    def bind(klass, *args, **kwargs):
        res = klass(*args, **kwargs)
        res.args.insert(0, res)
        return res

    def __repr__(self):
        try:
            call = _repr(self._callable_root)
            if self._callable_name is not None:
                call += ' :' + self._callable_name
            args = ', '.join(_repr(a) for a in self.args)
            kwargs = ', '.join(k+"="+_repr(v) for k, v in self.kwargs.items())
            if args:
                if kwargs:
                    args += ", " + kwargs
            else:
                args = kwargs
            return '<%s ``%s(%s)``>' % (_repr(self), call, args)
        except (TypeError, ValueError, AttributeError):
            # broken reprs are a bad idea; they obscure problems
            return super(Job, self).__repr__()

    @property
    def callable(self):
        if self._callable_name is None:
            return self._callable_root
        else:
            return getattr(self._callable_root, self._callable_name)
    @rwproperty.setproperty
    def callable(self, value):
        # can't pickle/persist methods by default as of this writing, so we
        # add the sugar ourselves.  In future, would like for args to be
        # potentially methods of persistent objects too...
        if self._status != zc.async.interfaces.NEW:
            raise zc.async.interfaces.BadStatusError(
                'can only set callable when a job has NEW, PENDING, or '
                'ASSIGNED status')
        if isinstance(value, types.MethodType):
            self._callable_root = value.im_self
            self._callable_name = value.__name__
        elif isinstance(value, zc.twist.METHOD_WRAPPER_TYPE):
            self._callable_root = zc.twist.get_self(value)
            self._callable_name = value.__name__
        else:
            self._callable_root, self._callable_name = value, None
        if zc.async.interfaces.IJob.providedBy(self._callable_root):
            self._callable_root.parent = self

    def addCallbacks(self, success=None, failure=None,
                     error_log_level=None, retry_policy=None):
        if success is not None or failure is not None:
            if success is not None:
                success = zc.async.interfaces.IJob(success)
                success.default_error_log_level = logging.CRITICAL
                if error_log_level is not None:
                    success.error_log_level = error_log_level
                success.default_retry_policy = 'callback'
                if retry_policy is not None:
                    success.retry_policy = retry_policy
            if failure is not None:
                failure = zc.async.interfaces.IJob(failure)
                failure.default_error_log_level = logging.CRITICAL
                if error_log_level is not None:
                    failure.error_log_level = error_log_level
                failure.default_retry_policy = 'callback'
                if retry_policy is not None:
                    failure.retry_policy = retry_policy
            res = Job(success_or_failure, success, failure)
            if success is not None:
                success.parent = res
            if failure is not None:
                failure.parent = res
            self.addCallback(res)
            # we need to handle the case of callbacks on the internal success/
            # failure jobs, to be safe.
            abort_handler = zc.async.interfaces.IJob(
                completeStartedJobArguments)
            abort_handler.args.append(res)
            res.addCallback(abort_handler, error_log_level)
            abort_handler.default_error_log_level = logging.CRITICAL
            if error_log_level is not None:
                abort_handler.error_log_level = error_log_level
            abort_handler.default_retry_policy = 'callback'
            if retry_policy is not None:
                abort_handler.retry_policy = retry_policy
        else:
            res = self
        return res

    def addCallback(self, callback, error_log_level=None, retry_policy=None):
        callback = zc.async.interfaces.IJob(callback)
        self.callbacks.put(callback)
        callback.parent = self
        if self._status == zc.async.interfaces.COMPLETED:
            callback(self.result) # this commits transactions!
        else:
            self._p_changed = True # to try and fire conflict errors if
            # our reading of self.status has changed beneath us
        callback.default_error_log_level = logging.CRITICAL
        if error_log_level is not None:
            callback.error_log_level = error_log_level
        callback.default_retry_policy = 'callback'
        if retry_policy is not None:
            callback.retry_policy = retry_policy
        return callback

    def _getRetry(self, call_name, tm, *args):
        def getRetry():
            retries = self.retries
            if retries is None:
                retry_policy = self.effective_retry_policy
                if retry_policy is None:
                    return None # means, do not retry ever
                elif isinstance(retry_policy, basestring):
                    retries = zope.component.getAdapter(
                        self, zc.async.interfaces.IRetries,
                        name=retry_policy)
                else:
                    retries = retry_policy(self)
                if retries is not None:
                    self.retries = retries
            call = getattr(retries, call_name, None)
            if call is None:
                zc.async.utils.log.error(
                    'retries %r for %r does not have required %s method',
                    retries, self, call_name)
                return None
            return call(*args)
        identifier = 'getting %s retry for %r' % (call_name, self)
        return zc.async.utils.never_fail(getRetry, identifier, tm)

    def __call__(self, *args, **kwargs):
        if self.status not in (zc.async.interfaces.NEW,
                               zc.async.interfaces.ASSIGNED):
            raise zc.async.interfaces.BadStatusError(
                'can only call a job with NEW or ASSIGNED status')
        tm = transaction.interfaces.ITransactionManager(self)
        self._status = zc.async.interfaces.ACTIVE
        self._active_start = datetime.datetime.now(pytz.UTC)
        tm.commit()
        effective_args = list(args)
        effective_args[0:0] = self.args
        effective_kwargs = dict(self.kwargs)
        effective_kwargs.update(kwargs)
        # this is the calling code.  It is complex and long because it is
        # trying both to handle exceptions reasonably, and to honor the
        # IRetries interface for those exceptions.
        data_cache = {}
        res = None
        while 1:
            try:
                res = self.callable(*effective_args, **effective_kwargs)
            except zc.async.utils.EXPLOSIVE_ERRORS:
                tm.abort()
                raise
            except:
                res = zc.twist.Failure()
                tm.abort()
                retry = self._getRetry('jobError', tm, res, data_cache)
                if isinstance(retry, (datetime.timedelta, datetime.datetime)):
                    identifier = (
                        'rescheduling %r as requested by '
                        'associated IRetries %r' % (
                            self, self.retries))
                    if self is zc.async.utils.never_fail(
                        lambda: self._reschedule(retry, data_cache),
                        identifier, tm):
                        return self
                elif retry:
                    continue
            try:
                self._set_result(res)
            except zc.async.utils.EXPLOSIVE_ERRORS:
                tm.abort()
                raise
            except:
                if isinstance(res, twisted.python.failure.Failure):
                    zc.async.utils.log.log(
                        self.effective_error_log_level,
                        'Commit failed for %r (see subsequent traceback).  '
                        'Prior to this, job originally failed with '
                        'traceback:\n%s',
                        self,
                        res.getTraceback(
                            elideFrameworkCode=True, detail='verbose'))
                else:
                    zc.async.utils.tracelog.info(
                        'Commit failed for %r (see subsequent traceback).  '
                        'Prior to this, job succeeded with result: %r',
                        self, res)
                res = zc.twist.Failure()
                tm.abort()
                retry = self._getRetry('jobError', tm, res, data_cache)
                if isinstance(retry, (datetime.timedelta, datetime.datetime)):
                    identifier = (
                        'rescheduling %r as requested by '
                        'associated IRetries %r' % (
                            self, self.retries))
                    if self is zc.async.utils.never_fail(
                        lambda: self._reschedule(retry, data_cache),
                        identifier, tm):
                        return self
                elif retry:
                    continue
                # retries didn't exist or returned False
                def complete():
                    self._result = res
                    self._status = zc.async.interfaces.CALLBACKS
                    self._active_end = datetime.datetime.now(pytz.UTC)
                    if self.retries is not None:
                        self.retries.updateData(data_cache)
                identifier = ('storing failure at commit of %r' % (self,))
                zc.async.utils.never_fail(complete, identifier, tm)
            self._complete(res)
            return res

    def handleInterrupt(self):
        # this is called either within a job (that has a never fail policy)
        # or withing _resumeCallbacks (that uses never_fail)
        if self.status is not zc.async.interfaces.ACTIVE:
            raise zc.async.interfaces.BadStatusError(
                'can only call ``handleInterrupt`` on a job with ACTIVE '
                'status')
        tm = transaction.interfaces.ITransactionManager(self)
        retry = self._getRetry('interrupted', tm)
        if retry:
            if not isinstance(retry, (datetime.timedelta, datetime.datetime)):
                retry = datetime.timedelta()
            self._reschedule(retry)
        else:
            self.fail()

    def _reschedule(self, retry, data_cache=None):
        if not zc.async.interfaces.IAgent.providedBy(self.parent):
            zc.async.utils.log.error(
                'error for IRetries %r on %r: '
                'can only reschedule a job directly in an agent',
                self.retries, self)
            return None
        self._status = zc.async.interfaces.NEW
        del self._active_start
        if data_cache is not None and self.retries is not None:
            self.retries.updateData(data_cache)
        self.parent.reschedule(self, retry)
        return self

    def _set_result(self, res):
        if zc.async.interfaces.IJob.providedBy(res):
            res.addCallback(self._callback)
        elif isinstance(res, twisted.internet.defer.Deferred):
            res.addBoth(zc.twist.Partial(self._callback))
            # XXX need to tell Partial to retry forever
        else:
            if isinstance(res, twisted.python.failure.Failure):
                res = zc.twist.sanitize(res)
            self._result = res
            self._status = zc.async.interfaces.CALLBACKS
            self._active_end = datetime.datetime.now(pytz.UTC)
        if self.retries is not None:
            self.retries.updateData(data_cache)
        tm.commit()

    def _complete(self, res):
        if isinstance(res, twisted.python.failure.Failure):
            zc.async.utils.log.log(
                self.effective_error_log_level,
                '%r failed with traceback:\n%s',
                self,
                res.getTraceback(
                    elideFrameworkCode=True, detail='verbose'))
        else:
            zc.async.utils.tracelog.info(
                '%r succeeded with result: %r',
                self, res)
        self.resumeCallbacks()

    def _callback(self, res):
        # done within a job or partial, so we can rely on their retry bits to
        # some degree.  However, we commit transactions ourselves, so we have
        # to be a bit careful that the result hasn't been set already.
        if self._status == zc.async.interfaces.ACTIVE:
            self._set_result(res)
        self._complete(res)

    def fail(self, e=None):
        if e is None:
            e = zc.async.interfaces.AbortedError()
        if self._status not in (zc.async.interfaces.NEW,
                                zc.async.interfaces.ACTIVE):
            raise zc.async.interfaces.BadStatusError(
                'can only call fail on a job with NEW, PENDING, ASSIGNED, or '
                'ACTIVE status')
        self._complete(zc.twist.Failure(e))

    def resumeCallbacks(self):
        if self._status != zc.async.interfaces.CALLBACKS:
            raise zc.async.interfaces.BadStatusError(
                'can only resumeCallbacks on a job with CALLBACKS status')
        identifier = 'performing callbacks for %r' % (self,)
        tm = transaction.interfaces.ITransactionManager(self)
        zc.async.utils.never_fail(self._resumeCallbacks, identifier, tm)

    def _resumeCallbacks(self):
        callbacks = list(self.callbacks)
        tm = transaction.interfaces.ITransactionManager(self)
        length = 0
        while 1:
            for j in callbacks:
                if j._status == zc.async.interfaces.NEW:
                    zc.async.utils.tracelog.debug(
                        'starting callback %r to %r', j, self)
                    j(self.result)
                elif j._status == zc.async.interfaces.ACTIVE:
                    zc.async.utils.tracelog.debug(
                        'failing aborted callback %r to %r', j, self)
                    j.handleInterrupt()
                elif j._status == zc.async.interfaces.CALLBACKS:
                    j.resumeCallbacks()
                # TODO: this shouldn't raise anything we want to catch, right?
                # now, this should catch all the errors except EXPLOSIVE_ERRORS
                # cleaning up dead jobs should look something like the above.
            tm.begin() # syncs
            # it's possible that someone added some callbacks, so run until
            # we're exhausted.
            length += len(callbacks)
            callbacks = list(self.callbacks)[length:]
            if not callbacks:
                # this whole method is called within a never_fail...
                self._status = zc.async.interfaces.COMPLETED
                if zc.async.interfaces.IAgent.providedBy(self.parent):
                    self.parent.jobCompleted(self)
                tm.commit()

