##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: dependable.py,v 1.3 2002/12/30 21:41:41 jeremy Exp $
"""

__metaclass__ = type

from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.annotation import IAnnotations
from zope.component import getAdapter

key = 'zope.app.dependable.Dependents'

class Dependable:
    __doc__ = IDependable.__doc__

    __implements__ =  IDependable

    def __init__(self, context):
        self.context = context

    def addDependent(self, location):
        "See IDependable"
        annotations = getAdapter(self.context, IAnnotations)
        annotations [key] = annotations.get(key, ()) + (location, )

    def removeDependent(self, location):
        "See IDependable"
        annotations = getAdapter(self.context, IAnnotations)
        annotations[key] = tuple([loc
                                  for loc in annotations.get(key, ())
                                  if loc != location])

    def dependents(self):
        "See IDependable"
        annotations = getAdapter(self.context, IAnnotations)
        return annotations.get(key, ())
