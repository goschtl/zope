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
"""Jobboard interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.interface import Attribute

class IJob(Interface):
    """Interface for the basic Job"""

    submitter = Attribute("submitter",
                          "Email address of the submitter")

    summary = Attribute("summary",
                        "One-line summary of the job")

    description = Attribute("description",
                            "Longer description of the job")

    contact = Attribute("contact",
                        "Email address to contact about the job")

    state = Attribute("state",
                      "Current state of the job listing.\n"
                      "The possible values are defined in JobState.")    

    salary = Attribute("salary",
                       "Salary range offered for the job.")

    startdate = Attribute("startdate",
                          "Job start date")

    def approve():
        "Moves the job state to Approved"


class JobState:
    """Possible values of IJob.state."""
    PendingApproval = "pending approval"
    Approved = "approved"
    

class IJobList(Interface):

    def __getitem__(jobid):
        """Returns the job with the given jobid"""

    def query(state):
        """Returns a list of Job ids"""

    def getApprovedIds():
        """Returns a sequence of ids for job that are in the approved state
        """

    def getPendingIds():
        """Returns a sequence of ids for jobs that are in the pending state
        """

    def add(job):
        """Add a Job object to the list.

        Returns the id assigned to the job.
        """

    def __delitem__(jobid):
        """Removes the Job object with the given id from the list.

        Raises KeyError if the jobid is not in the list.
        """
