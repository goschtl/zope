##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Undo view

$Id: browser.py,v 1.1 2004/03/01 14:16:56 philikon Exp $
"""
from zope.app import zapi
from zope.app.undo.interfaces import IUndoManager

class UndoView:
    """Undo view
    """

    def action(self, id_list):
        """processes undo form and redirects to form again (if possible)"""
        utility = zapi.getUtility(self.context, IUndoManager)
        utility.undoTransaction(id_list)
        self.request.response.redirect('index.html')

    def getUndoInfo(self, first=0, last=-20, user_name=None):
        utility = zapi.getUtility(self.context, IUndoManager)
        info = utility.getUndoInfo(first, last, user_name)
        formatter = self.request.locale.dates.getFormatter('dateTime', 'medium')
        for entry in info:
            entry['datetime'] = formatter.format(entry['datetime'])
        return info
