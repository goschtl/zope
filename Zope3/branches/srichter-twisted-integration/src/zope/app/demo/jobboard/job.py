##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Job implementation

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from interfaces import IJob, JobState, IJobList
from zope.interface import implements


class Job(Persistent):
    """ Job Class

    >>> myJob = Job(submitter='my name', summary='my summary',
    ...             description='my description',contact='my contact',
    ...             salary='111', startdate='10/01/2003')
    >>> myJob.summary
    'my summary'
    >>> myJob.state
    'pending approval'
    >>> myJob.approve()
    >>> myJob.state
    'approved'
    """
    
    implements(IJob)
   
        
    def __init__(self, submitter, summary, description,
                 contact, salary=None, startdate=None):
        self.submitter = submitter
        self.summary = summary
        self.description = description
        self.contact = contact
        self.state = JobState.PendingApproval
        self.salary = salary
        self.startdate = startdate

    def approve(self):
        """Moves the job state to approved"""
        self.state = JobState.Approved



##########################################################################



from persistent.dict import PersistentDict

class JobList(Persistent):
    """ the Joblist class manages the creation, deletion of job list and
    can display the object ids which are in specific states

    >>> from job import Job
    >>> joblist = JobList()
    >>> myJob1 = Job(submitter='my name', summary='my summary',
    ...             description='my description',contact='my contact',
    ...             salary='111', startdate='10/01/2003')
    >>> myJob2 = Job(submitter='my name2', summary='my summary2',
    ...             description='my description2',contact='my contact2',
    ...             salary='222', startdate='20/12/2003')

    >>> joblist.add(myJob1)
    '1'
    >>> joblist.add(myJob2)
    '2'
    >>> joblist.getPendingIds()
    ['1', '2']
    >>> joblist.query('pending approval')
    ['1', '2']
    >>> myJob1.approve()
    >>> joblist.getPendingIds()
    ['2']
    >>> joblist.getApprovedIds()
    ['1']
    """
    implements(IJobList)


    def __init__(self):
        self._lastid = 0
        self._jobs = PersistentDict()

    def add(self, job):
        self._lastid += 1
        jobid = self._lastid
        self._jobs[jobid] = job
        # stringified for parity with query
        # this can return an int when query can also return an int
        return str(jobid)

    def __delitem__(self, jobid):
        # accept stringified job ids, see add()
        try:
            jobid = int(jobid)
        except ValueError:
            raise KeyError, jobid
        del self._jobs[jobid]

    def query(self, state):
        ids = [jobid
               for jobid, job in self._jobs.items()
               if job.state == state]
        ids.sort()
        # this should work returning a list of ints,
        # but it exposes a bug in PageTemplates
        return map(str, ids)

    def __getitem__(self, jobid):
        # accept stringified job ids, see add()
        try:
            jobid = int(jobid)
        except ValueError:
            raise KeyError, jobid
        return self._jobs[jobid]

    def getPendingIds(self):
        return self.query(JobState.PendingApproval)
        
        
    def allIds(self):
        return  self._jobs.items()
        #ids.sort()
        # this should work returning a list of ints,
        # but it exposes a bug in PageTemplates
        #return map(str, ids)

    def getApprovedIds(self):
        return self.query(JobState.Approved)
