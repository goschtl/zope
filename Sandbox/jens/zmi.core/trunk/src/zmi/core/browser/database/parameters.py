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
ZODB Parameters
"""

class View(object):

    # dummy variables
    database_size = "database_size"
    cache_extreme_detail = {'oid':'Object ID', 'klass':'Object Class',
                            'rc':'Reference Count', 'references':'References'}
    cache_detail_length = ()
    database_size = "database_size"
    cache_length = "cache_length"
    cache_length_bytes = "cache_length_bytes"
    cache_detail = {'key':'Cache Key', 'value': 'Cache Value'}

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.index()