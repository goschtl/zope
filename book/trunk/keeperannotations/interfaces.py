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
"""Interfaces for an Annotation Keeper

$Id$
"""
from zope.interface import Interface
from zope.app.annotation.interfaces import IAnnotatable
  
class IAnnotationKeeper(Interface):
    """Marker indicating that an object is willing to store other object's
    annotations in its own annotations.
    
    This interface makes only sense, if the object that implements this
    interface also implements 'IAnnotatable' or any sub-class.
    """
  
class IKeeperAnnotatable(IAnnotatable):
    """Marker indicating that an object will store its annotations in an
    object implementing IAnnotationKeeper.
  
    This requires the object that provides this interface to also implement
    ILocation.
    
    This interface does not specify how the keeper may be found. This is up
    to the adapter that uses this interface to provide 'IAnnotations'.
    """
