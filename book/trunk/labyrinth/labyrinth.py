##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Labyrinth Game

This example of Zope 3's security was inspired by the
zope.security.example. Unfortunately, this code did more than necessary and
was therefore inappropriate for a book example. This is a much thinner version. 

$Id: labyrinth.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
class Person(object):

    def __init__(self, id):
        self.id = id
        self.room = None

    def goTo(self, direction):
        assert direction in ('north', 'south', 'east', 'west'), \
               '"%s" is not a valid direction' %direction
        room = getattr(self.room, direction, None)
        if room is None:
            print 'There is no room %s of here.' %direction
        else:
            print room.description
            self.room = room
        

class Room(object):

    def __init__(self, id, description):
        self.id = id
        self.description = description
        self.north = self.south = self.east = self.west = None


def setupWorld():
    # Create the rooms
    entrance = Room('entrance', 'The entrance of the labyrinth')
    fork = Room('fork', 'The big decision. Do I go east or west.')
    stairs = Room('stairs', 'Some long dark stairs.')
    hall = Room('hall', 'A cathedral-like hall.')
    corridor = Room('corridor', 'A long corridor')

    # Connect the rooms
    entrance.north = fork
    fork.south, fork.west, fork.east = entrance, stairs, corridor
    stairs.east, stairs.north = fork, hall
    corridor.west, corridor.north = fork, hall
    hall.west, hall.east = stairs, corridor

    # Setup player 
    player = Person('player')
    player.room = entrance
    return player


def main():
    player = setupWorld()
    command = ''
    while command != 'exit':
        try:
            if command == 'info':
                print player.room.description
            elif command:
                player.goTo(command)

        except Exception, e:
            print '%s: %s' %(e.__class__.__name__, e)

        command = raw_input('Command: ')


if __name__ == '__main__':
    main()
