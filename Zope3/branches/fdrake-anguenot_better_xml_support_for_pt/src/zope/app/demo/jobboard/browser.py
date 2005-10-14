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
"""Jobboard browser views

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent


from job import Job

class JobCreateView(BrowserView):
    """ class to create job entries

    >>> from job import JobList
    >>> from zope.publisher.browser import TestRequest
    >>> from zope.app.testing.placelesssetup import setUp, tearDown
    >>> setUp()
    >>> class TestJobList:
    ...    context = None
    ...    def add(self, myObj):
    ...         self.tempStorage = myObj

    >>> 
    >>> request = TestRequest()
    >>> joblist = TestJobList()
    >>> view = JobCreateView(joblist, request)
    >>> myThanksPage = view.create(submitter='sree', summary='my job summary',
    ...                  description='my desc', contact = 'sree')
    >>> joblist.tempStorage.summary
    'my job summary'
    >>> tearDown()
    """
    edit = ViewPageTemplateFile('edit.pt')

    preview = ViewPageTemplateFile('preview.pt')

    thanks = ViewPageTemplateFile('thanks.pt')

    def create(self, submitter='', summary='', description='', contact=''):
        # Validation code should go here
        job = Job(submitter, summary, description, contact)
        self.context.add(job)
        notify(ObjectModifiedEvent(self.context))
        return self.thanks()
        
        
################################

class ApproveJobsView(BrowserView):
    """ class to Approve existing job entries

    >>> from job import JobList
    >>> from zope.publisher.browser import TestRequest
    >>> from zope.app.testing.placelesssetup import setUp, tearDown
    >>> setUp()
    >>> 
    >>> request = TestRequest(form={'1':'approve','2':'discard'})
    >>> class TestJobList:
    ...    context = None
    ...    tempStorage = []
    ...    def add(self, myObj):
    ...         self.tempStorage.append( myObj)

    >>> joblist = JobList()

    >>> view = JobCreateView(joblist, request)
    >>> myThanksPage = view.create(submitter='sree', summary='my job summary',
    ...                  description='my desc', contact = 'sree')
    >>> myThanksPage = view.create(submitter='sree2', summary='my summaryy2',
    ...                  description='my desc2', contact = 'sree2')
    >>> approvedview = ApproveJobsView(joblist, request)
    >>> approvedview.approve()
    >>> request.response.getHeader('location')
    '.'
    >>> joblist['1'].state
    'approved'
    >>> joblist['2'].state
    Traceback (most recent call last):
    ...
    KeyError: 2
    >>> tearDown()
    """
    review = ViewPageTemplateFile('review.pt')

    def approve(self):
        form = self.request.form

        for jobid in form:
            try:
               job = self.context[jobid]
            except:
               pass

            action = form[jobid]
            if action == 'approve':
                job.approve()
            elif action == 'discard':
                del self.context[jobid]

        response = self.request.response
        if self.context.getPendingIds():
            response.redirect('review.html')
        else:
            response.redirect('.')
        notify(ObjectModifiedEvent(self.context))

