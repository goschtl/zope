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
$Id: undo.py,v 1.3 2003/01/20 19:58:57 jim Exp $
"""
from zope.component import getUtility
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.interfaces.undo import IUndoManager


class ZODBUndoManager:
    """Implement the basic undo management api for a single ZODB database.
    """

    __implements__ =  IUndoManager

    def __init__(self, db):
        self.__db = db

    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.undo.IUndoManager.

    def getUndoInfo(self):
        '''See interface IUndoManager'''

        return self.__db.undoInfo()

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

    def getUndoInfo(self):
        utility = getUtility(self.context, IUndoManager)
        return utility.getUndoInfo()
