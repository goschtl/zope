##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interfaces for filesystem synchronization.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope import interface
from zope import component
from zope import annotation

class IFSSyncAnnotations(annotation.interfaces.IAnnotations):
    """Access to synchronizable annotations."""
    
    def __iter__():
        """Iterates over the package-unique keys."""

class IFSSyncFactory(component.interfaces.IFactory):
    """A factory for file-system representation adapters.
    
    This factory should be registered as a named utility with the dotted name of 
    the adapted class as the lookup key. 
    
    The default factory should be registered without a name.
    
    The call of the factory should return
    
    - an `IDirectoryEntry` adapter for the object if the
      object is represented as a directory on the file system.

    - an `IFileEntry` adapter for the object if the
      object is represented as a file on the file system.

    or

    - default, if no special synchronizser has been registered.
    
    See registration.txt for further explanations.
    """
    
