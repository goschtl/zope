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

from zope.app.xmlrpcintrospection.xmlrpcintrospection import xmlrpccallable
from zope.app.publisher.xmlrpc import XMLRPCView

class RemoteTaskServiceXMLRPCAPI(XMLRPCView):
    """An XML-RPC API for the external Remote Task Service API."""

    @xmlrpccallable(list)
    def getAvailableTasks(self):
        """Get all available tasks that the service provides.

        The result will be a list of task names.
        """
        return sorted(self.context.getAvailableTasks().keys())

    @xmlrpccallable(int, str, dict)
    def add(self, task, input):
        """Add a new job to the service.

        The result will be the id of the new job.
        """
        return self.context.add(unicode(task), input)

    @xmlrpccallable(bool, int)
    def cancel(self, jobid):
        """Cancel a job from execution.

        The result is meaningless.
        """
        self.context.cancel(jobid)
        return True

    @xmlrpccallable(str, int)
    def getStatus(self, jobid):
        """Get the status of the current job.

        The return value is a string representing the status.
        """
        return self.context.getStatus(jobid)

    @xmlrpccallable(dict, int)
    def getResult(self, jobid):
        """Get the result of the job execution.

        The return value will be a dictionary of return values. The content of
        the dictionary will vary with every task.
        """
        return self.context.getResult(jobid)

    @xmlrpccallable(str, int)
    def getError(self, jobid):
        """Get the error from a failed job execution.

        The return value will be an error message that describes the failure.
        """
        return self.context.getError(jobid)
