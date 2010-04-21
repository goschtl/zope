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
from z3c.taskqueue.service import TaskService
from z3c.taskqueue.startup import databaseOpened
from z3c.taskqueue.startup import getStartSpecifications


def bootStrapSubscriber(event):
    databaseOpened(event, productName='lovely.remotetask')


def getAutostartServiceNames():
    from zope.app.appsetup.product import getProductConfiguration
    configuration = getProductConfiguration('lovely.remotetask')
    return getStartSpecifications(configuration)
