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
"""
$Id$
"""
from zope.app.event.interfaces import ISubscriber
from zope.interface import Interface

class ICatalogIndexUpdate(ISubscriber):
    "A wrapper around an Index that's in a Catalog"

    def clear():
        "Clear everything from the index"

class ICatalogIndexQuery(Interface):
    "la la la la la"

    def search(term): 
        "do a search"

class ICatalogIndex(ICatalogIndexUpdate, ICatalogIndexQuery): 
    pass

