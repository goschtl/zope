##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: ResultSet.py,v 1.1 2002/06/25 15:41:45 k_vertigo Exp $
"""

class ResultSet(list): 

    def __init__(self, names, data, row_klass):
        self.names = names
        self.row_klass = row_klass
        super(ResultSet).__init__(self, data)

    def __getitem__(self, idx):
        return self.row_klass(list.__getitem__(idx))
    
    


