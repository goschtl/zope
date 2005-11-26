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
"""Tutorials-related Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.app.container import interfaces, constraints


class ITutorialManager(interfaces.IReadContainer):
    """Tutorial Manager

    The tutorial manager is used as an entry point to the tutorials
    application.
    """


class ITutorial(zope.interface.Interface):
    """Tutorial

    Tutorials are objects that provide a tutorial via the browser to a
    user. They use functional test-browser tests for their content.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the tutorial.',
        required=True)

    path = zope.schema.URI(
        title=u'File Path',
        description=u'Path to the file used for the tutorial',
        required=True)


class ITutorialSessionManager(interfaces.IContainer):
    """Tutorial Session Manager

    The tutorial sessoin manager keeps track of all sessions for a given
    tutorial.
    """
    constraints.contains('.ITutorialSession')

    def createSession():
        """Create a session and return its name."""

    def deleteSession(name):
        """Delete a session for the given name."""


class ITutorialSession(interfaces.IContained):
    """Tutorial Session

    The session keeps track of the state of the tutorial for the user.
    """
    constraints.containers(ITutorialSessionManager)

    locked = zope.schema.Bool(
        title=u'Locked',
        description=u'Specifies whether the session is locked.',
        default=False)

    def initialize():
        """Initialize the session."""

    def addCommand(command):
        """Add a command to the commands queue.

        This method should also create and return a unique command id that is
        used to associate the result with.
        """

    def getCommand():
        """Return the next command in the queue.

        This method returns the command id and the command itself. The
        returned command must be removed from the queue. ``(None, None)`` is
        returned, if no command is in the queue.
        """

    def addResult(id, result):
        """Add a result for a command.

        The id identifies the command this result is for.
        """

    def getResult(id):
        """Get result for a given command id.
        """

    def keepGoing():
        """Return whether the system should keep going processing events.

        The method should return False, when the parts switch from a string to
        an example and vice versa.
        """

    def setTimeout(seconds):
        """Set a timeout for a result to be returned or the next command to be
        retrieved."""
