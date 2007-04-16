##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Task Service Implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import datetime
import persistent
import threading
import time
import zc.queue
import zope.component
import zope.interface
import zope.publisher.base
import zope.publisher.publish
from BTrees.IOBTree import IOBTree
from BTrees.IFBTree import IFTreeSet
from zope.security.proxy import removeSecurityProxy
from zope.traversing.api import traverse
from zope.app import zapi
from zope.app.container import contained
from zope.app.publication.zopepublication import ZopePublication
from lovely.remotetask import interfaces, job, task


class TaskService(contained.Contained, persistent.Persistent):
    """A persistent task service.

    The available tasks for this service are managed as utilities.
    """
    zope.interface.implements(interfaces.ITaskService)

    taskInterface = interfaces.ITask

    def __init__(self):
        super(TaskService, self).__init__()
        self._counter = 1
        self.jobs = IOBTree()
        self._queue = zc.queue.PersistentQueue()
        self._scheduledJobs = IOBTree()
        self._scheduledQueue = zc.queue.PersistentQueue()

    def getAvailableTasks(self):
        """See interfaces.ITaskService"""
        return dict(zope.component.getUtilitiesFor(self.taskInterface))

    def add(self, task, input=None):
        """See interfaces.ITaskService"""
        if task not in self.getAvailableTasks():
            raise ValueError('Task does not exist')
        jobid = self._counter
        self._counter += 1
        newjob = job.Job(jobid, task, input)
        self.jobs[jobid] = newjob
        self._queue.put(newjob)
        newjob.status = interfaces.QUEUED
        return jobid

    def addCronJob(self, task, input=None,
                   minute=(),
                   hour=(),
                   dayOfMonth=(),
                   month=(),
                   dayOfWeek=(),
                  ):
        jobid = self._counter
        self._counter += 1
        newjob = job.CronJob(jobid, task, input,
                minute, hour, dayOfMonth, month, dayOfWeek)
        self.jobs[jobid] = newjob
        self._scheduledQueue.put(newjob)
        newjob.status = interfaces.CRONJOB
        return jobid

    def clean(self, stati=[interfaces.CANCELLED, interfaces.ERROR,
                           interfaces.COMPLETED]):
        """See interfaces.ITaskService"""
        allowed = [interfaces.CANCELLED, interfaces.ERROR,
                   interfaces.COMPLETED]
        for key in list(self.jobs.keys()):
            job = self.jobs[key]
            if job.status in stati:
                if job.status not in allowed:
                    raise ValueError('Not allowed status for removing. %s' % \
                        job.status)
                del self.jobs[key]

    def cancel(self, jobid):
        """See interfaces.ITaskService"""
        for idx, job in enumerate(self._queue):
            if job.id == jobid:
                job.status = interfaces.CANCELLED
                self._queue.pull(idx)
                break

    def getStatus(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].status

    def getResult(self, jobid):
        """See interfaces.ITaskService"""
        return self.jobs[jobid].output

    def getError(self, jobid):
        """See interfaces.ITaskService"""
        return str(self.jobs[jobid].error)

    def startProcessing(self):
        """See interfaces.ITaskService"""
        path = [parent.__name__ for parent in zapi.getParents(self)
                 if parent.__name__]
        path.reverse()
        path.append(self.__name__)
        path.append('processNext')

        thread = threading.Thread(
            target=processor, args=(self._p_jar.db(), path),
            name='remotetasks.'+self.__name__)
        thread.running = True
        thread.start()

    def stopProcessing(self):
        """See interfaces.ITaskService"""
        name = 'remotetasks.'+self.__name__
        for thread in threading.enumerate():
            if thread.getName() == name:
                thread.running = False
                break

    def isProcessing(self):
        """See interfaces.ITaskService"""
        name = 'remotetasks.' + self.__name__
        for thread in threading.enumerate():
            if thread.getName() == name:
                if thread.running:
                    return True
        return False

    def processNext(self, now=None):
        job = self._pullJob(now)
        if job is None:
            return False
        jobtask = zope.component.getUtility(
                        self.taskInterface, name=job.task)
        job.started = datetime.datetime.now()
        try:
            job.output = jobtask(self, job.id, job.input)
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.COMPLETED
        except task.TaskError, error:
            job.error = error
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.ERROR
        job.completed = datetime.datetime.now()
        return True

    def process(self, now=None):
        """See interfaces.ITaskService"""
        while self.processNext(now):
            pass

    def _pullJob(self, now=None):
        # first move new cron jobs from the scheduled queue into the cronjob
        # list
        if now is None:
            now = time.time()
        while len(self._scheduledQueue)>0:
            job = self._scheduledQueue.pull()
            if job.status is not interfaces.CANCELLED:
                self._insertCronJob(job, now)
        while True:
            try:
                first = self._scheduledJobs.minKey()
            except ValueError:
                break
            else:
                if first > now:
                    break
                jobs = self._scheduledJobs[first]
                job = jobs[0]
                self._scheduledJobs[first] = jobs[1:]
                if len(self._scheduledJobs[first]) == 0:
                    del self._scheduledJobs[first]
                self._insertCronJob(job, now)
                if job.status != interfaces.CANCELLED:
                    return job
        if self._queue:
            return self._queue.pull()
        return None

    def _insertCronJob(self, job, now):
        nextCallTime = job.timeOfNextCall(now)
        set = self._scheduledJobs.get(nextCallTime)
        if set is None:
            self._scheduledJobs[nextCallTime] = ()
        jobs = self._scheduledJobs[nextCallTime]
        self._scheduledJobs[nextCallTime] = jobs + (job,)


class ProcessorPublication(ZopePublication):
    """A custom publication to process the next job."""

    def traverseName(self, request, ob, name):
        return traverse(removeSecurityProxy(ob), name, None)


def processor(db, path):
    """Job Processor

    Process the jobs that are waiting in the queue. This processor is meant to
    be run in a separate process; however, it simply goes back to the task
    service to actually do the processing.
    """
    path.reverse()
    while threading.currentThread().running:
        request = zope.publisher.base.BaseRequest(None, {})
        request.setPublication(ProcessorPublication(db))
        request.setTraversalStack(path)
        try:
            zope.publisher.publish.publish(request, False)
        except IndexError:
            time.sleep(1)
        except:
            # This thread should never crash, thus a blank except
            pass
