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
Revision information: 
$Id: OrderedFolder.py,v 1.2 2002/06/10 23:28:00 jim Exp $

"""

from Zope.App.OFS.Container.IOrderedContainer import IOrderedContainer
from types import StringType


class OrderedFolder:
    """Adds the Ordering Feature to a Folder
    """

    __implements__ = IOrderedContainer

    _orderedIds = ()


    def moveObjectsByPositions(self, ids, positionDelta):
        """ """

        if type(ids) is StringType:
            ids = (ids,)

        # Interestingly enough, we need to switch the order when
        # moving, so that the movements won't cancel each
        # other
        if positionDelta > 0:
            ids = list(ids)
            ids.reverse()
            
        moved_objects = 0
        
        for id in ids:
            old_position = self.getObjectPosition(id)
            new_position = old_position + positionDelta
            # Make sure the new position makes sense and is valid
            if not (old_position == new_position  or
                    new_position > len(self) or
                    new_position < 0):
                
                id_list = list(self._orderedIds)
                # now delete the entry ...
                id_list.remove(id)
                # ... and now add it again
                id_list.insert(new_position, id)
                self._orderedIds = tuple(id_list)

                moved_objects += 1

        return moved_objects


    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.IOrderedContainer

    def getObjectPosition(self, id):
        '''See interface IOrderedContainer'''

        if id in self._orderedIds:
            return list(self._orderedIds).index(id)
        else:
            # If the object was not found, throw an error.
            # Yeah, that is good raise 'ObjectNotFound',
            raise ( 'ObjectNotFound',
                    'The object named %s was not found.' %id)


    def moveObjectsDown(self, ids):
        '''See interface IOrderedContainer'''
        return self.moveObjectsByPositions(ids, +1)


    def moveObjectsUp(self, ids):
        '''See interface IOrderedContainer'''
        return self.moveObjectsByPositions(ids, -1)


    def moveObjectsToTop(self, ids):
        '''See interface IOrderedContainer'''
        if type(ids) is StringType:
            ids = (ids,)

        position_delta = - self.getObjectPosition(ids[0])
        return self.moveObjectsByPositions(ids, position_delta)


    def moveObjectsToBottom(self, ids):
        '''See interface IOrderedContainer'''
        if type(ids) is StringType:
            ids = (ids,)

        # Whee, we will do the reverse twice, but for going to the bottom
        # there is no other choice.
        ids = list(ids)
        ids.reverse()

        position_delta = len(self) - self.getObjectPosition(ids[-1]) - 1

        return self.moveObjectsByPositions(ids, position_delta)


    def moveObjectToPosition(self, id, position):
        '''See interface IOrderedContainer'''
        return self.moveObjectsByPositions(id,
                   position - self.getObjectPosition(id))

    #
    ############################################################

