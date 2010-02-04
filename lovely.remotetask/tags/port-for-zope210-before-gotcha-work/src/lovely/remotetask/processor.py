##############################################################################
#
# Copyright (c) 2006, 2007 Lovely Systems and Contributors.
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
"""Processor Implementations

$Id$
"""
__docformat__ = 'restructuredtext'
import logging
import threading
import time
import transaction
import zope.interface
import zope.publisher.base
import zope.publisher.publish
from zope.app.publication.zopepublication import ZopePublication
from zope.security import management
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import traverse

try:
    from ZPublisher.HTTPRequest import HTTPRequest
    from ZPublisher.HTTPResponse import HTTPResponse
    import ZPublisher
    from types import StringType
    ZOPE2=True
except ImportError:
    ZOPE2=False

from lovely.remotetask import interfaces

THREAD_STARTUP_WAIT = 0.05

ERROR_MARKER = object()

log = logging.getLogger('lovely.remotetask')


class ProcessorPublication(ZopePublication):
    """A custom publication to process the next job."""

    def beforeTraversal(self, request):
        # Overwrite this method, so that the publication does not attempt to
        # authenticate; we assume that the processor is allowed to do
        # everything. Note that the DB is not exposed to the job callable.
        management.newInteraction(request)
        transaction.begin()

    def traverseName(self, request, ob, name):
        # Provide a very simple traversal mechanism.
        return traverse(removeSecurityProxy(ob), name, None)

class ProcessorRequest(zope.publisher.base.BaseRequest):
    """A custome publisher request for the processor."""

    def __init__(self, *args):
        super(ProcessorRequest, self).__init__(None, {}, positional=args)


class SimpleProcessor(object):
    """Simple Job Processor

    This processor only processes one job at a time.
    """
    zope.interface.implements(interfaces.IProcessor)

    @property
    def running(self):
        thread = threading.currentThread()
        if thread is not None:
            return thread.running
        log.error('SimpleProcessor: no currentThread')
        return False

    def __init__(self, db, servicePath, waitTime=1.0):
        self.db = db
        self.servicePath = servicePath
        self.waitTime = waitTime

    def call(self, method, args=(), errorValue=ERROR_MARKER):
        # Create the path to the method.
        path = self.servicePath[:] + [method]
        path.reverse()
        # Produce a special processor event to be sent to the publisher.
        request = ProcessorRequest(*args)
        request.setPublication(ProcessorPublication(self.db))
        request.setTraversalStack(path)
        # Publish the request, making sure that *all* exceptions are
        # handled. The processor should *never* crash.
        try:
            zope.publisher.publish.publish(request, False)
            return request.response._result
        except Exception, error:
            # This thread should never crash, thus a blank except
            log.error('Processor: ``%s()`` caused an error!' %method)
            log.exception(error)
            return errorValue is ERROR_MARKER and error or errorValue
            
    def processNext(self, jobid=None):
        return self.call('processNext', args=(None, jobid))

    def __call__(self):
        while self.running:
            result = self.processNext()
            # If there are no jobs available, sleep a little bit and then
            # check again.
            if not result:
                time.sleep(self.waitTime)

class SimpleZope2Processor(SimpleProcessor):
    """ SimpleProcessor for Zope2 """
    
    zope.interface.implements(interfaces.IProcessor)

    def call(self, method, args=(), errorValue=ERROR_MARKER):
        path = [method] + self.servicePath[:]
        path.reverse()
        response = HTTPResponse()
        env = { 'SERVER_NAME': 'dummy',
                'SERVER_PORT': '8080',
                'PATH_INFO': '/' + '/'.join(path) }
        request = HTTPRequest(None, env, response)
        conn = self.db.open()
        root = conn.root()
        request['PARENTS'] = [root[ZopePublication.root_name]]
        try:
            try:
                ZPublisher.Publish.publish(request,'Zope2', [None])
            except Exception, error:
                # This thread should never crash, thus a blank except
                log.error('Processor: ``%s()`` caused an error!' %method)
                log.exception(error)
                return errorValue is ERROR_MARKER and error or errorValue
        finally:
            request.close()
            conn.close()
            if not request.response.body:
                time.sleep(1)
            else:
                return request.response.body

class MultiProcessor(SimpleProcessor):
    """Multi-threaded Job Processor

    This processor can work on multiple jobs at the same time.
    """
    zope.interface.implements(interfaces.IProcessor)

    def __init__(self, *args, **kwargs):
        self.maxThreads = kwargs.pop('maxThreads', 5)
        super(MultiProcessor, self).__init__(*args, **kwargs)
        self.threads = []

    def hasJobsWaiting(self):
        return self.call('hasJobsWaiting', errorValue=False)

    def claimNextJob(self):
        return self.call('claimNextJob', errorValue=None)

    def __call__(self):
        # Start the processing loop
        while self.running:
            # Remove all dead threads
            for thread in self.threads:
                if not thread.isAlive():
                    self.threads.remove(thread)
            # If the number of threads equals the number of maximum threads,
            # wait a little bit and then start over
            if len(self.threads) == self.maxThreads:
                time.sleep(self.waitTime)
                continue
            # Let's wait for jobs to become available
            while not self.hasJobsWaiting() and self.running:
                time.sleep(self.waitTime)
            # Okay, we have to do some work, so let's do that now. Since we
            # are working with threads, we first have to claim a job and then
            # execute it.
            jobid = self.claimNextJob()
            # If we got a job, let's work on it in a new thread.
            if jobid is not None:
                thread = threading.Thread(
                    target=self.processNext, args=(jobid,))
                self.threads.append(thread)
                thread.start()
                # Give the thread some time to start up:
                time.sleep(THREAD_STARTUP_WAIT)

class MultiZope2Processor(MultiProcessor, SimpleZope2Processor):
    """Multi-threaded Job Processor

    This processor can work on multiple jobs at the same time.
    
    WARNING: This still does not work correctly in Zope2
    """
    zope.interface.implements(interfaces.IProcessor)

    def __init__(self, *args, **kwargs):
        self.maxThreads = kwargs.pop('maxThreads', 5)
        super(MultiZope2Processor, self).__init__(*args, **kwargs)
        self.threads = []

    def hasJobsWaiting(self):
        value = self.call('hasJobsWaiting', errorValue=False)
        if isinstance(value, StringType):
            if value == 'True':
                return True
            else:
                return False
        return value

    def claimNextJob(self):
        value = self.call('claimNextJob', errorValue=None)
        try:
            value = int(value)
        except ValueError:
            pass
        return value
