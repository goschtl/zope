##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
$Id: undo.py,v 1.3 2004/03/18 14:33:21 philikon Exp $
"""
from datetime import datetime
from zope.interface import implements

from zope.app import zapi
from zope.app.event import function
from zope.app.undo.interfaces import IUndoManager
from zope.app.servicenames import Utilities

def undoSetup(event):
    # setup undo functionality
    svc = zapi.getService(None, Utilities)
    svc.provideUtility(IUndoManager, ZODBUndoManager(event.database))

undoSetup = function.Subscriber(undoSetup)

class ZODBUndoManager:
    """Implement the basic undo management api for a single ZODB database."""
    implements(IUndoManager)

    def __init__(self, db):
        self.__db = db

    def getUndoInfo(self, first=0, last=-20, user_name=None):
        """See zope.app.undo.interfaces.IUndoManager"""

        # Entries are a list of dictionaries, containing
        # id          -> internal id for zodb
        # user_name   -> name of user that last accessed the file
        # time        -> unix timestamp of last access
        # description -> transaction description

        if user_name is not None:

            # XXX The 'user' in the transactions is a concatenation of
            # 'path' and 'user' (id). 'path' used to be the path of
            # the user folder in Zope 2. ZopePublication currently
            # does not set a path, so it defaults to '/'. Maybe we can
            # find a new meaning for 'path' in Zope 3 (the principal
            # source?)
            path = '/' # default for now
            specification = {'user_name': path + ' ' + user_name}
        else:
            specification = None
        entries = self.__db.undoInfo(first, last, specification)

        # We walk through the entries, augmenting the dictionaries 
        # with some additional items (at the moment, datetime, a useful 
        # form of the unix timestamp).
        for e in entries:
            e['datetime'] = datetime.fromtimestamp(e['time'])
        return entries

    def undoTransaction(self, id_list):
        '''See zope.app.undo.interfaces.IUndoManager'''

        for id in id_list:
            self.__db.undo(id)
