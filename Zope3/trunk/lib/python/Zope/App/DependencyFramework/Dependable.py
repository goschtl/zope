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
$Id: Dependable.py,v 1.2 2002/11/18 22:25:16 jim Exp $
"""

__metaclass__ = type

from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.OFS.Annotation.IAnnotations \
     import IAnnotations
from Zope.ComponentArchitecture import getAdapter

key = 'Zope.App.DependencyFramework.Dependents'

class Dependable:
    __doc__ = IDependable.__doc__

    __implements__ =  IDependable

    def __init__(self, context):
        self.context = context
        

    def addDependent(self, location):
        "See Zope.App.DependencyFramework.IDependable.IDependable"
        annotations = getAdapter(self.context, IAnnotations)
        annotations [key] = annotations.get(key, ()) + (location, )

    def removeDependent(self, location):
        "See Zope.App.DependencyFramework.IDependable.IDependable"
        annotations = getAdapter(self.context, IAnnotations)
        annotations[key] = tuple([loc
                                  for loc in annotations.get(key, ())
                                  if loc != location])

    def dependents(self):
        "See Zope.App.DependencyFramework.IDependable.IDependable"
        annotations = getAdapter(self.context, IAnnotations)
        return annotations.get(key, ())
