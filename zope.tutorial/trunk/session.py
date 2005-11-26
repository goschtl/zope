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
import thread
import types
import time
import types
import zope.proxy
import zope.testbrowser
from zope.app import annotation
from zope.app import zapi
from zope.app import container
from zope.app.apidoc.utilities import renderText
from zope.app.component import hooks
from zope.app.location import location

from zope.tutorial import interfaces
from zope.tutorial import testbrowser

NORESULT = object()
NOACTION = {'action': 'nullAction', 'params': ()}

SESSIONMANAGER_CACHE = {}


class BrowserBroker(object):

    def __init__(self, session):
        self.session = session

    def executeAction(self, action, *args):
        id = self.session.addCommand({'action': action, 'params': args})
        # wait for the answer to come in
        result = NORESULT
        while result is NORESULT:
            time.sleep(0.1)
            result = self.session.getResult(id)

        return result

    def __getattr__(self, name):
        def action(*args):
            return self.executeAction(name, *args)
        return action


def run(session, example):
    """Run a doctest example."""

    def BrowserFactory(url=None):
        return testbrowser.Browser(BrowserBroker(session), url)

    OldBrowser = zope.testbrowser.Browser
    zope.testbrowser.Browser = BrowserFactory
    exec compile(example.source, '<string>', "single") in session.globals
    session.locked = False
    zope.testbrowser.Browser = OldBrowser


class TutorialSession(location.Location):
    """Tutorial Session"""
    zope.component.adapts(interfaces.ITutorial)
    zope.interface.implements(interfaces.ITutorialSession)

    locked = False

    def __init__(self, tutorialName):
        self.tutorialName = tutorialName
        self._commandCounter = 0

    def initialize(self):
        """See interfaces.ITutorialSession"""
        # Create a parts stack
        tutorial = zapi.getUtility(interfaces.ITutorial, name=self.tutorialName)
        text = open(tutorial.path, 'r').read()
        parser = doctest.DocTestParser()
        parts = parser.parse(text)

        # Clean up the parts by removing empty strings
        self._parts = [
            part for part in parts
            if not isinstance(part, types.StringTypes) or part.strip()]
        self._parts.reverse()
        self._current = None

        # Setup actions
        self._commands = []
        self._results = {}

        # The global variables of the execution environment
        self.globals = {}

    def addCommand(self, command):
        """See interfaces.ITutorialSession"""
        name = u'command-' + unicode(self._commandCounter)
        self._commandCounter += 1
        self._commands.append((name, command))
        return name

    def getCommand(self):
        """See interfaces.ITutorialSession"""
        if len(self._commands):
            return self._commands.pop()

        if not len(self._parts):
            self.addCommand({'action': 'finishTutorial',
                             'params': ()})
            return self._commands.pop()

        part = self._current = self._parts.pop()
        if isinstance(part, types.StringTypes):
            text = renderText(part, format='zope.source.rest')
            self.addCommand({'action': 'displayText',
                             'params': (text,)})
            return self._commands.pop()
        else:
            self.locked = True
            thread.start_new_thread(run, (self, part))
            while self.locked and not len(self._commands):
                time.sleep(0.1)

            # The part was executed without creating any command
            if not self.locked:
                return (None, NOACTION)

            return self._commands.pop()

    def addResult(self, id, result):
        """See interfaces.ITutorialSession"""
        self._results[id] = result

    def getResult(self, name):
        """See interfaces.ITutorialSession"""
        return self._results.pop(name, NORESULT)

    def keepGoing(self):
        """See interfaces.ITutorialSession"""
        if len(self._parts) == 0:
            return False
        return type(self._current) == type(self._parts[-1])


class TutorialSessionManager(container.btree.BTreeContainer):
    """A session manager based on BTrees."""
    zope.component.adapter(interfaces.ITutorial)
    zope.interface.implements(interfaces.ITutorialSessionManager)

    def __init__(self):
        super(TutorialSessionManager, self).__init__()

    def createSession(self):
        session = TutorialSession(zapi.getName(self))
        chooser = container.interfaces.INameChooser(self)
        name = chooser.chooseName(u'session', session)
        self[name] = session
        return name

    def deleteSession(self, name):
        del self[name]


class sessionsNamespace(object):
    """Used to traverse the `++sessions++` namespace"""

    def __init__(self, ob=None, request=None):
        tutorialName = zapi.name(ob)
        manager = SESSIONMANAGER_CACHE.get(tutorialName)
        if manager is None:
            manager = TutorialSessionManager()
            location.locate(manager, ob, tutorialName)
            SESSIONMANAGER_CACHE[tutorialName] = manager

        self.sessionManager = manager

    def traverse(self, name, ignore=None):
        if name == '':
            return self.sessionManager
        else:
            return self.sessionManager[name]
