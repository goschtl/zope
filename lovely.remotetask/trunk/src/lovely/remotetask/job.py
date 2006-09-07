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
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from lovely.remotetask import interfaces


class Job(persistent.Persistent):
    """A simple, non-persistent task implementation."""
    zope.interface.implements(interfaces.IJob)

    id = FieldProperty(interfaces.IJob['id'])
    task = FieldProperty(interfaces.IJob['task'])
    status = FieldProperty(interfaces.IJob['status'])
    input = FieldProperty(interfaces.IJob['input'])
    output = FieldProperty(interfaces.IJob['output'])
    error = FieldProperty(interfaces.IJob['error'])
    created = FieldProperty(interfaces.IJob['created'])
    started = FieldProperty(interfaces.IJob['started'])
    completed = FieldProperty(interfaces.IJob['completed'])

    def __init__(self, id, task, input):
        self.id = id
        self.task = task
        self.input = input
        self.created = datetime.datetime.now()

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.id)
