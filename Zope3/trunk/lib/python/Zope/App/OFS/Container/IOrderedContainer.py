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
  $Id: IOrderedContainer.py,v 1.3 2002/10/04 17:46:49 jim Exp $
"""

from Interface import Interface

class IReadOrderedContainer(Interface):


    def getObjectPosition(id):
        """Get the position of the object having the id.
        """

Read = IReadOrderedContainer
    
class IWriteOrderedContainer(Interface):


    def moveObjectToPosition(id, position):
        """Move an object having id to position.
        """
        

    def moveObjectsUp(ids):
        """Move the specified objects (via ids) one field up.
        """

    
    def moveObjectsDown(ids):
        """Move the specified objects (via ids) one field down.
        """


    def moveObjectsToTop(ids):
        """Move the specified objects (via ids) to the top.
        """


    def moveObjectsToBottom(ids):
        """Move the specified objects (via ids) to the bottom.
        """

Write = IWriteOrderedContainer

class IOrderedContainer(IReadOrderedContainer, IWriteOrderedContainer):
    """This interface adds functionality to containers that will allow
       sorting of the contained items.
       
    """
