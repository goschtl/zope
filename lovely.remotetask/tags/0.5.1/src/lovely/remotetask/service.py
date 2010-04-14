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
"""Task Service Implementation

"""
__docformat__ = 'restructuredtext'

from lovely.remotetask import interfaces, job, task, processor
from zope import component
from zope.app.appsetup.product import getProductConfiguration
from zope.app.container import contained
from zope.app.publication.zopepublication import ZopePublication
from zope.component.interfaces import ComponentLookupError
from zope.traversing.api import getParents
import BTrees
import datetime
import logging
import persistent
import random
import threading
import time
import zc.queue
import zope.interface
import zope.location


log = logging.getLogger('lovely.remotetask')

storage = threading.local()


class TaskService(contained.Contained, persistent.Persistent):
    """A persistent task service.

    The available tasks for this service are managed as utilities.
    """
    zope.interface.implements(interfaces.ITaskService)

    taskInterface = interfaces.ITask
    processorFactory = processor.SimpleProcessor
    processorArguments = {'waitTime': 1.0}

    _scheduledJobs  = None
    _scheduledQueue = None
    _v_nextid = None
    family = BTrees.family32

    def __init__(self):
        super(TaskService, self).__init__()
        self.jobs = self.family.IO.BTree()
        self._queue = zc.queue.Queue()
        self._scheduledJobs = self.family.IO.BTree()
        self._scheduledQueue = zc.queue.Queue()

    def getAvailableTasks(self):
        """See interfaces.ITaskService"""
        return dict(component.getUtilitiesFor(self.taskInterface))

    def add(self, task, input=None, startLater=False):
        """See interfaces.ITaskService"""
        if task not in self.getAvailableTasks():
            raise ValueError('Task does not exist')
        jobid = self._generateId()
        newjob = job.Job(jobid, task, input)
        self.jobs[jobid] = newjob
        if startLater:
            newjob.status = interfaces.STARTLATER
        else:
            self._queue.put(newjob)
            newjob.status = interfaces.QUEUED
        return jobid

    def addCronJob(self, task, input=None,
                   minute=(),
                   hour=(),
                   dayOfMonth=(),
                   month=(),
                   dayOfWeek=(),
                   delay=None,
                  ):
        jobid = self._generateId()
        newjob = job.CronJob(jobid, task, input,
                minute, hour, dayOfMonth, month, dayOfWeek, delay)
        self.jobs[jobid] = newjob
        if newjob.delay is None:
            newjob.status = interfaces.CRONJOB
        else:
            newjob.status = interfaces.DELAYED
        self._scheduledQueue.put(newjob)
        return jobid

    def startJob(self, jobid):
        job = self.jobs[jobid]
        if job.status == interfaces.STARTLATER:
            self._queue.put(job)
            job.status = interfaces.QUEUED
            return True
        return False

    def reschedule(self, jobid):
        self._scheduledQueue.put(self.jobs[jobid])

    def clean(self, status=[interfaces.CANCELLED, interfaces.ERROR,
                            interfaces.COMPLETED]):
        """See interfaces.ITaskService"""
        allowed = [interfaces.CANCELLED, interfaces.ERROR,
                   interfaces.COMPLETED]
        for key in list(self.jobs.keys()):
            job = self.jobs[key]
            if job.status in status:
                if job.status not in allowed:
                    raise ValueError('Not allowed status for removing. %s' %
                        job.status)
                del self.jobs[key]

    def cancel(self, jobid):
        """See interfaces.ITaskService"""
        for idx, job in enumerate(self._queue):
            if job.id == jobid:
                job.status = interfaces.CANCELLED
                self._queue.pull(idx)
                break
        if jobid in self.jobs:
            job = self.jobs[jobid]
            if (   job.status == interfaces.CRONJOB
                or job.status == interfaces.DELAYED
                or job.status == interfaces.STARTLATER
               ):
                job.status = interfaces.CANCELLED

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
        if self.__parent__ is None:
            return
        if self._scheduledJobs is None:
            self._scheduledJobs = self.family.IOB.Tree()
        if self._scheduledQueue is None:
            self._scheduledQueue = zc.queue.PersistentQueue()
        # Create the path to the service within the DB.
        servicePath = [parent.__name__ for parent in getParents(self)
                       if parent.__name__]
        servicePath.reverse()
        servicePath.append(self.__name__)
        # Start the thread running the processor inside.
        processor = self.processorFactory(
            self._p_jar.db(), servicePath, **self.processorArguments)
        thread = threading.Thread(target=processor, name=self._threadName())
        thread.setDaemon(True)
        thread.running = True
        thread.start()

    def stopProcessing(self):
        """See interfaces.ITaskService"""
        if self.__name__ is None:
            return
        name = self._threadName()
        for thread in threading.enumerate():
            if thread.getName() == name:
                thread.running = False
                break

    def isProcessing(self):
        """See interfaces.ITaskService"""
        if self.__name__ is not None:
            name = self._threadName()
            for thread in threading.enumerate():
                if thread.getName() == name:
                    if thread.running:
                        return True
                    break
        return False

    def _threadName(self):
        """Return name of the processing thread."""
        # This name isn't unique based on the path to self, but this doesn't
        # change the name that's been used in past versions.
        path = [parent.__name__ for parent in getParents(self)
                if parent.__name__]
        path.append('remotetasks')
        path.reverse()
        path.append(self.__name__)
        return '.'.join(path)

    def hasJobsWaiting(self, now=None):
        # If there is are any simple jobs in the queue, we have work to do.
        if self._queue:
            return True
        # First, move new cron jobs from the scheduled queue into the cronjob
        # list.
        if now is None:
            now = int(time.time())
        while len(self._scheduledQueue) > 0:
            job = self._scheduledQueue.pull()
            if job.status is not interfaces.CANCELLED:
                self._insertCronJob(job, now)
        # Now get all jobs that should be done now or earlier; if there are
        # any that do not have errors or are cancelled, then we have jobs to
        # do.
        for key in self._scheduledJobs.keys(max=now):
            jobs = [job for job in self._scheduledJobs[key]
                    if job.status not in (interfaces.CANCELLED,
                                          interfaces.ERROR)]
            if jobs:
                return True
        return False

    def claimNextJob(self, now=None):
        job = self._pullJob(now)
        return job and job.id or None

    def processNext(self, now=None, jobid=None):
        if jobid is None:
            job = self._pullJob(now)
        else:
            job = self.jobs[jobid]
        if job is None:
            return False
        if job.status == interfaces.COMPLETED:
            return True
        try:
            jobtask = component.getUtility(self.taskInterface, name=job.task)
        except ComponentLookupError, error:
            log.error('Task "%s" not found!'% job.task)
            log.exception(str(error))
            job.error = error
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.ERROR
            return True
        job.started = datetime.datetime.now()
        if not hasattr(storage, 'runCount'):
            storage.runCount = 0
        storage.runCount += 1
        try:
            job.output = jobtask(self, job.id, job.input)
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.COMPLETED
        except task.TaskError, error:
            job.error = error
            if job.status != interfaces.CRONJOB:
                job.status = interfaces.ERROR
        except Exception, error:
            if storage.runCount <= 3:
                log.error('Caught a generic exception, preventing thread '
                          'from crashing')
                log.exception(str(error))
                raise
            else:
                job.error = error
                if job.status != interfaces.CRONJOB:
                    job.status = interfaces.ERROR
        job.completed = datetime.datetime.now()
        storage.runCount = 0
        return True

    def process(self, now=None):
        """See interfaces.ITaskService"""
        while self.processNext(now):
            pass

    def _pullJob(self, now=None):
        # first move new cron jobs from the scheduled queue into the cronjob
        # list
        if now is None:
            now = int(time.time())
        while len(self._scheduledQueue) > 0:
            job = self._scheduledQueue.pull()
            if job.status is not interfaces.CANCELLED:
                self._insertCronJob(job, now)
        # try to get the next cron job
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
                if (    job.status != interfaces.CANCELLED
                    and job.status != interfaces.ERROR
                   ):
                    if job.status != interfaces.DELAYED:
                        self._insertCronJob(job, now)
                    return job
        # get a job from the input queue
        if self._queue:
            return self._queue.pull()
        return None

    def _insertCronJob(self, job, now):
        for callTime, scheduled in list(self._scheduledJobs.items()):
            if job in scheduled:
                scheduled = list(scheduled)
                scheduled.remove(job)
                if len(scheduled) == 0:
                    del self._scheduledJobs[callTime]
                else:
                    self._scheduledJobs[callTime] = tuple(scheduled)
                break
        nextCallTime = job.timeOfNextCall(now)
        job.scheduledFor = datetime.datetime.fromtimestamp(nextCallTime)
        set = self._scheduledJobs.get(nextCallTime)
        if set is None:
            self._scheduledJobs[nextCallTime] = ()
        jobs = self._scheduledJobs[nextCallTime]
        self._scheduledJobs[nextCallTime] = jobs + (job,)

    def _generateId(self):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = random.randrange(0, self.family.maxint)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self.jobs:
                return uid
            self._v_nextid = None



def getAutostartServiceNames():
    """get a list of services to start"""

    serviceNames = []
    config = getProductConfiguration('lovely.remotetask')
    if config is not None:
        serviceNames = [name.strip()
                        for name in config.get('autostart', '').split(',')]
    return serviceNames


def bootStrapSubscriber(event):
    """Start the queue processing services based on the
       settings in zope.conf"""

    serviceNames = getAutostartServiceNames()

    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    # we assume that portals can only added at site root level

    log.info('handling event IStartRemoteTasksEvent')

    for siteName, serviceName in [name.split('@')
                                  for name in serviceNames if name]:
        if siteName == '':
            sites = [root_folder]
        elif siteName == '*':
            sites = []
            sites.append(root_folder)
            for folder in root_folder.values():
                if zope.location.interfaces.ISite.providedBy(folder):
                    sites.append(folder)
        else:
            sites = [root_folder.get(siteName)]

        rootSM = root_folder.getSiteManager()
        rootServices = list(rootSM.getUtilitiesFor(interfaces.ITaskService))

        for site in sites:
            csName = getattr(site, "__name__", '')
            if csName is None:
                csName = 'root'
            if site is not None:
                sm = site.getSiteManager()
                if serviceName == '*':
                    services = list(sm.getUtilitiesFor(interfaces.ITaskService))
                    if siteName != "*" and siteName != '':
                        services = [s for s in services
                                       if s not in rootServices]
                else:
                    services = [(serviceName,
                                 component.queryUtility(interfaces.ITaskService,
                                                       context=site,
                                                       name=serviceName))]
                serviceCount = 0
                for srvname, service in services:
                    if service is not None and not service.isProcessing():
                        service.startProcessing()
                        serviceCount += 1
                        msg = 'service %s on site %s started'
                        log.info(msg % (srvname, csName))
                    else:
                        if siteName != "*" and serviceName != "*":
                            msg = 'service %s on site %s not found'
                            log.error(msg % (srvname, csName))
            else:
                log.error('site %s not found' % siteName)

        if (siteName == "*" or serviceName == "*") and serviceCount == 0:
            msg = 'no services started by directive %s'
            log.warn(msg % name)
