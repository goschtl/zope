##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import persistent

from zope import component
from zope import interface

from zope.app.container.contained import Contained

from lovely import remotetask

from lovely.mail import sendmail as standardmail
from lovely.remotetask.interfaces import ITask, ITaskService


class RemoteMail(persistent.Persistent, Contained):
    """ Task for remote mail """
    interface.implements(ITask)

    def __call__(self, service, jobid, input):
        standardmail( **input )


def sendmail(subject, fromaddr, toaddrs, body, replyTo=None, bodytype='plain', delay=None):
    """overloaded lovely.mail.sendmail function"""
    
    if delay is None:
        standardmail(subject, fromaddr, toaddrs, body, replyTo, bodytype)
        return
    
    service = component.getUtility( ITaskService )
    service.addCronJob( u'remotemail', {
            'subject':subject,
             'fromaddr':fromaddr,
             'toaddrs':toaddrs,
             'body':body,
             'replyTo':replyTo,
             'bodytype':bodytype },
             delay=delay )
    
    
