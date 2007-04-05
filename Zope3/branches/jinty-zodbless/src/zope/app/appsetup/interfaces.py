##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""API for working installing things on startup.

$Id$
"""

from zope import interface
from zope.app.publication.interfaces import IResourceFactory


class IDatabaseOpenedEvent(interface.Interface):
    """The main database has been opened."""

    database = interface.Attribute("The main database.")

class DatabaseOpened(object):
    interface.implements(IDatabaseOpenedEvent)

    def __init__(self, database):
        self.database = database

class IDatabaseOpenedWithRootEvent(interface.Interface):
    """The main database has been opened."""

    database = interface.Attribute("The main database.")

class DatabaseOpenedWithRoot(object):
    interface.implements(IDatabaseOpenedWithRootEvent)

    def __init__(self, database):
        self.database = database

class IProcessStartingEvent(interface.Interface):
    """The application server process is starting."""

class ProcessStarting(object):
    interface.implements(IProcessStartingEvent)

class IApplicationFactory(IResourceFactory):

    def prepare(self):
        """Prepare the application object factory.

        This must be called once, after the component architecture
        has been loaded.
        """
