##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Tutorial Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import doctest
import os
import persistent
import types
import zope.component
import zope.interface

from zope.tutorial import interfaces


class Tutorial(object):
    """Tutorial"""
    zope.interface.implements(interfaces.ITutorial)

    def __init__(self, title, path):
        self.title = title
        self.path = path

    def __repr__(self):
        return '<%s title=%r, file=%r>' %(
            self.__class__.__name__, self.title, os.path.split(self.path)[-1])


class TutorialSession(persistent.Persistent):
    """Tutorial Session"""

    zope.component.adapts(interfaces.ITutorial)
    #zope.interface.implements(interfaces.ITutorialSession)

    def __init__(self, tutorial):
        self.tutorial = tutorial


    def initialize(self):
        """See interfaces.ITutorialSession"""
        text = open(self.tutorial.path, 'r').read()
        parser = doctest.DocTestParser()
        self.parts = parser.parse(text)
        # Clean up the parts by removing empty strings
        self.parts = [part for part in self.parts
                      if (not isinstance(part, types.StringTypes) or
                          part.strip())]
        # Create a parts stack
        self.parts.reverse()

        # Set some runtime variables
        self.globs = {}


    def getNextStep(self):
        """See interfaces.ITutorialSession"""
        try:
            return self.parts.pop()
        except IndexError:
            return None
