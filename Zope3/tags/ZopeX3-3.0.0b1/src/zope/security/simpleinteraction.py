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
""" Define Zope\'s default interaction class

$Id$
"""

import sets

from zope.interface import implements
from zope.security.interfaces import IInteraction

__metaclass__ = type


class Interaction:
    implements(IInteraction)

    def __init__(self):
        self.participations = []

    def add(self, participation):
        if participation.interaction is not None:
            raise ValueError("%r already belongs to an interaction"
                             % participation)
        participation.interaction = self
        self.participations.append(participation)

    def remove(self, participation):
        if participation.interaction is not self:
            raise ValueError("%r does not belong to this interaction"
                             % participation)
        self.participations.remove(participation)
        participation.interaction = None


def createInteraction(participation=None):
    """A helper for implementing ISecurityPolicy.createInteraction"""
    interaction = Interaction()
    if participation is not None:
        interaction.add(participation)
    return interaction

