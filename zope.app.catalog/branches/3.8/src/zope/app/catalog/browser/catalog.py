##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Catalog Views

$Id$
"""
from zope.catalog.interfaces import ICatalog

class Advanced:
    "Provides a user interface for configuring a catalog"

    __used_for__ = ICatalog

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def reindex(self):
        self.context.clear()
        self.context.updateIndexes()
        self.request.response.redirect('@@advanced.html')
