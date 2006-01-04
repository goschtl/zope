##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Task Management objects for Zope 3

$Id$
"""
__docformat__ = "reStructuredText"

from zope.app import zapi
from scheduler import interfaces

def startAllTasks(event):
    for name, task in zapi.getUtilitiesFor(interfaces.ITask):
        task.start()

def stopAllTasks(event):
    for name, task in zapi.getUtilitiesFor(interfaces.ITask):
        task.stop()
    
