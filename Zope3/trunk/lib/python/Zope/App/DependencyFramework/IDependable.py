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
$Id: IDependable.py,v 1.1 2002/10/14 11:51:05 jim Exp $
"""

from Interface import Interface

class IDependable(Interface):
   """Objects that can have dependencies
   """

   def addDependent(location):
       """Add a dependency to a dependent object by location

       The location is the physical path to the object.
       """
   def removeDependent(location):
       """Remove a dependency with a dependent object by location.

       The location is the physical path to the object.
       """
   def dependents():
       """Return a sequence of dependent object locations.
       """
__doc__ = IDependable.__doc__ + __doc__
