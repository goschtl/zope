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
$Id: ZODBUndoManager.py,v 1.2 2002/06/10 23:28:17 jim Exp $
"""
from Zope.App.Undo.IUndoManager import IUndoManager


class ZODBUndoManager:
    """Implement the basic undo management api for a single ZODB database.
    """
    
    __implements__ =  IUndoManager

    def __init__(self, db):
        self.__db = db

    ############################################################
    # Implementation methods for interface
    # Zope.App.Undo.IUndoManager.

    def getUndoInfo(self):
        '''See interface IUndoManager'''
        
        return self.__db.undoInfo()

    def undoTransaction(self, id_list):
        '''See interface IUndoManager'''

        for id in id_list:
            self.__db.undo(id)

    #
    ############################################################

