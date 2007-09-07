##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding

from lovely.rating.interfaces import IRatingDefinition
from lovely.rating.scoresystem import SimpleScoreSystem


def evolveToSimpleScoreSystem(context):
    """This is a help to migrate existing rating definitions.

    It only works if you use a score system which is compatible with
    SimpleScoreSystem.
    It is meant to be used from your application evolve script.
    """
    for definition in findObjectsProviding(
            getRootFolder(context), IRatingDefinition):
        old = definition.scoreSystem
        new = SimpleScoreSystem(
                old.__name__, old.title, old.description, old.scores)
        definition.scoreSystem = new

