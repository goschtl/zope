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

from Interface import Interface

class IUndoManager(Interface):
    " Interface for the Undo Manager "
   
    def getUndoInfo():
        """ 
        Gets all undo information.
        Note: at the moment, doesnt care where called from

        returns sequence of mapping objects by date desc
                
        keys of mapping objects:
          id          -> internal id for zodb
          user_name   -> name of user that last accessed the file
          time        -> date of last access
          description -> transaction description
        """


    def undoTransaction(id_list):
        """
        id_list will be a list of transaction ids.
        iterate over each id in list, and undo
        the transaction item.
        """

