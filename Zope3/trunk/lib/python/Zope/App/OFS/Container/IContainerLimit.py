##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
  $Id: IContainerLimit.py,v 1.2 2002/06/10 23:27:55 jim Exp $
"""

from Interface import Interface

class IReadContainerLimit(Interface):


    def getLimit():
        """Get the maximal amount of possible objects in this container.
        """


    def isLimitReached():
        """Returns a boolean describing whether the folder reached its maximal
           amount of objects."""

class IWriteContainerLimit(Interface):


    def setLimit(limit):
        """Set the maximal amount of possible objects in this container.
        """

class IContainerLimit(IReadContainerLimit, IWriteContainerLimit):
    """This interface adds a specific functionality to a container by
       specifying the limiting amount of objects in a container.

       NOTE: This interface expects that the IReadContainer interface.
    """
    
        
