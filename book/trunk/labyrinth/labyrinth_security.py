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
"""Secure Labyrinth Simulation

This example of Zope 3's security was inspired by the
zope.security.example. Unfortunately, this code did more than necessary and
was therefore inappropriate for a book example. This is a much thinner version. 

$Id: labyrinth_security.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
import labyrinth
from zope.interface import implements
from zope.security.interfaces import IParticipation
from zope.security import checker, management, simplepolicies

Allow = 'allow'

permissions = {}

def allowPerson(roomid, personid):
    """Allow a particular person in a room."""
    perms = permissions.setdefault(roomid, [])
    perms.append(personid)


class PersonParticipation(object):

    implements(IParticipation)

    def __init__(self, person):
        self.principal = person
        self.interaction = None


class SecurityPolicy(simplepolicies.ParanoidSecurityPolicy):
    """The Labyrinth's access security policy."""

    def checkPermission(self, permission, object):
        """See zope.security.interfaces.ISecurityPolicy"""
        assert permission is Allow 
        allowed = permissions.get(object.id, [])
        for participation in self.participations:
            if not participation.principal.id in allowed:
                return False
        return True


def setupSecurity(player):
    # Setup security
    management.setSecurityPolicy(SecurityPolicy)
    room_checker = checker.NamesChecker(
        ('description', 'north', 'south', 'west', 'east'), Allow)
    checker.defineChecker(labyrinth.Room, room_checker)

    # Allow the player everywhere but the corridor
    allowPerson('entrance', player.id)
    allowPerson('fork', player.id)
    allowPerson('stairs', player.id)
    allowPerson('hall', player.id)

    # Add the player as a security manager and provide the player with a
    # secure room
    management.newInteraction(PersonParticipation(player))
    proxied_room = checker.selectChecker(player.room).proxy(player.room)
    player.room = proxied_room
    return player


if __name__ == '__main__':
    oldSetupWorld = labyrinth.setupWorld
    labyrinth.setupWorld = lambda : setupSecurity(oldSetupWorld())
    labyrinth.main()
