##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
$Id$
"""
__docformat__ = "reStructuredText"

from zope import interface
from zope import schema

class IResponseCacheSettings(interface.Interface):

    key = schema.BytesLine(title=u'Cachekey', required=True)

    cacheName = schema.TextLine(title=u'Cachename',
                                required=False,
                                default=u'')

    lifetime = schema.Int(title = u'Lifetime',
                          required = False,
                          )

    dependencies = schema.List(title=u'Dependencies',
                               required=False,
                               default=[])


class IPurge(interface.Interface):

    def purge(expr, escapes='+-'):
        """Method to purge the hosts with the given expression"""


class IPurgeView(interface.Interface):
    """Schema for the purge view"""

    expression = schema.TextLine(title=u'expression',
                                 description=u'Expression to purge',
                                 required=True)
