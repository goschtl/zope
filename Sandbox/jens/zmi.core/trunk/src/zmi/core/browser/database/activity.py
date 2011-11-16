##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
ZODB Activity
"""

class View(object):

    # dummy variables for bootstrapping view
    getHistoryLength = 1
    start_time = "start_time"
    end_time = "end_time"
    divs = ()
    connections = "connections"
    trans_len = "trans_len"
    store_len = "store_len"
    load_len = "load_len"
    total_store_count = "total_store_count"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.index()