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
import zope.proxy
from zope.app import annotation
from zope.app import zapi
from zope.app.component import hooks
from zope.app.container import btree
from zope.app.location import location

from zope.tutorial import interfaces


SessionManagerKey = 'zope.tutorial.SessionManager'


class Tutorial(object):
    """Tutorial"""
    zope.interface.implements(interfaces.ITutorial)

    def __init__(self, title, path):
        self.title = title
        self.path = path

    def __repr__(self):
        return '<%s title=%r, file=%r>' %(
            self.__class__.__name__, self.title, os.path.split(self.path)[-1])


class TutorialSession(persistent.Persistent, location.Location):
    """Tutorial Session"""

    zope.component.adapts(interfaces.ITutorial)
    zope.interface.implements(interfaces.ITutorialSession)

    locked = False

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
        self.current = None

        # Set some runtime variables
        self.globs = {}

    def getNextStep(self):
        """See interfaces.ITutorialSession"""
        if self.locked:
            return None
        try:
            self.current = self.parts.pop()
        except IndexError:
            self.current = None
            return None

        return self.current

    def keepGoing(self):
        return type(self.parts[-1]) == type(self.current)


class TutorialSessionManager(btree.BTreeContainer):
    """A session manager based on BTrees."""
    zope.component.adapter(interfaces.ITutorial)
    zope.interface.implements(interfaces.ITutorialSessionManager)

    def __init__(self):
        super(TutorialSessionManager, self).__init__()
        self.__counter = 0

    def createSession(self):
        name = unicode(self.__counter)
        self[name] = TutorialSession(zapi.getParent(self))
        self.__counter += 1;
        return name

    def deleteSession(self, name):
        del self[name]


class sessionsNamespace(object):
    """Used to traverse the `++sessions++` namespace"""

    def __init__(self, ob=None, request=None):
        site = hooks.getSite()
        annotations = annotation.interfaces.IAnnotations(site)
        manager = annotations.get(SessionManagerKey)

        if manager is None:
            manager = TutorialSessionManager()
            tutorial = zope.proxy.removeAllProxies(ob)
            location.locate(manager, tutorial, '++sessions++')
            annotations[SessionManagerKey] = manager

        self.sessionManager = manager


    def traverse(self, name, ignore=None):
        if name == '':
            return self.sessionManager
        else:
            return self.sessionManager[name]
