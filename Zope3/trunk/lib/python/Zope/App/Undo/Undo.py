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

from Zope.ComponentArchitecture import getUtility
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.PageTemplate import ViewPageTemplateFile
from IUndoManager import IUndoManager


class Undo(BrowserView):
    " Undo View "

    def __init__(self, *args):
        super(Undo, self).__init__(*args)
        self.utility = getUtility(self.context, IUndoManager)
        
    index = ViewPageTemplateFile('undo_log.pt')


    def action (self, id_list, REQUEST=None):
        """
        processes undo form and redirects to form again (if possible)
        """
        self.utility.undoTransaction(id_list)
        
        if REQUEST is not None:
            REQUEST.response.redirect('index.html')
            


    def getUndoInfo(self):
        return self.utility.getUndoInfo()

