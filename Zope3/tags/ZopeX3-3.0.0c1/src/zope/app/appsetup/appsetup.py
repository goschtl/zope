##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Code to initialize the application server

$Id$
"""
import zope.interface
from zope.security.interfaces import IParticipation
from zope.security.management import system_user

class IDatabaseOpenedEvent(zope.interface.Interface):
    """The main database has been opened."""

    database = zope.interface.Attribute("The main database.")

class DatabaseOpened(object):
    zope.interface.implements(IDatabaseOpenedEvent)

    def __init__(self, database):
        self.database = database

class IProcessStartingEvent(zope.interface.Interface):
    """The application server process is starting."""

class ProcessStarting(object):
    zope.interface.implements(IProcessStartingEvent)

class SystemConfigurationParticipation(object):
    zope.interface.implements(IParticipation)

    principal = system_user
    interaction = None

_configured = False
def config(file, execute=True):
    """Configure site globals"""
    global _configured
    global __config_source
    __config_source = file

    if _configured:
        return

    from zope.configuration import xmlconfig

    # Set user to system_user, so we can do anything we want
    from zope.security.management import newInteraction
    newInteraction(SystemConfigurationParticipation())

    # Load server-independent site config
    context = xmlconfig.file(file, execute=execute)

    # Reset user
    from zope.security.management import endInteraction
    endInteraction()

    _configured = execute

    return context

def database(db):
    """Load ZODB database from Python module or FileStorage file"""
    if type(db) is str:
        # Database name
        if db.endswith('.py'):
            # Python source, exec it
            globals = {}
            execfile(db, globals)
            if 'DB' in globals:
                db = globals['DB']
            else:
                storage = globals['Storage']
                from ZODB.DB import DB
                db = DB(storage, cache_size=4000)
        elif db.endswith(".fs"):
            from ZODB.FileStorage import FileStorage
            from ZODB.DB import DB
            storage = FileStorage(db)
            db = DB(storage, cache_size=4000)

    # The following will fail unless the application has been configured.
    from zope.event import notify
    notify(DatabaseOpened(db))

    return db


__config_source = None
def getConfigSource():
    return __config_source
