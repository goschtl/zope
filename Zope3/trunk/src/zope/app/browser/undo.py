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

Revision information:
$Id: undo.py,v 1.7 2003/07/10 12:42:12 anthony Exp $
"""
from zope.interface import implements
from zope.component import getService, getUtility
from zope.publisher.browser import BrowserView
from zope.app.event import function
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.interfaces.undo import IUndoManager
from zope.app.services.servicenames import Utilities
from datetime import datetime


def undoSetup(event):
    # setup undo fnctionality
    svc = getService(None, Utilities)
    svc.provideUtility(IUndoManager, ZODBUndoManager(event.database))

undoSetup = function.Subscriber(undoSetup)


class ZODBUndoManager:
    """Implement the basic undo management api for a single ZODB database.
    """

    implements(IUndoManager)

    def __init__(self, db):
        self.__db = db

    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.undo.IUndoManager.

    def getUndoInfo(self, first=0, last=-20, user_name=None):
        '''See interface IUndoManager'''

        # Entries are a list of dictionaries, containing
        # id          -> internal id for zodb
        # user_name   -> name of user that last accessed the file
        # time        -> unix timestamp of last access
        # description -> transaction description

        if user_name is not None:
            # !?&%!! The 'user' in the transactions is some combination
            # of 'path' and 'user'. 'path' seems to only ever be '/' at
            # the moment - I can't find anything that calls it :-(
            # At the moment the path is hacked onto the user_name in the 
            # PageTemplate 'undo_log.pt' (to minimise the nastiness).
            specification = {'user_name':user_name}
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
        '''See interface IUndoManager'''

        for id in id_list:
            self.__db.undo(id)

    #
    ############################################################


class Undo(BrowserView):
    """Undo View"""

    index = ViewPageTemplateFile('undo_log.pt')

    def action (self, id_list, REQUEST=None):
        """
        processes undo form and redirects to form again (if possible)
        """
        utility = getUtility(self.context, IUndoManager)
        utility.undoTransaction(id_list)

        if REQUEST is not None:
            REQUEST.response.redirect('index.html')

    def getUndoInfo(self, first=0, last=-20, user_name=None):
        utility = getUtility(self.context, IUndoManager)
        return utility.getUndoInfo(first, last, user_name)
