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
"""The connection adapters contained by ConnectionService.

$Id: ZopeDatabaseAdapter.py,v 1.2 2002/06/25 15:41:45 k_vertigo Exp $
"""

from Zope.Configuration.name import resolve
from Persistence import Persistent
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter
class ZopeDatabaseAdapter(Persistent):

    __implements__ = IZopeDatabaseAdapter
    _v_connection =  None

    def __init__(self, id, title, factory, user, password, host, database):
        self.id       = id
        self.title    = title
        self.factory  = factory
        self.user     = user
        self.password = password
        self.host     = host
        self.database = database
        
    def __call__(self):

        if self._v_connection is not None:
            return self._v_connection

        factory = resolve(self.factory)
        self._v_connection = factory(user=self.user,
                                     password=self.password,
                                     host=self.host,
                                     database=self.database)
        return self._v_connection



