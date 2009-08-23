##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

from z3c.bobopublisher.interfaces import IPublishTraverse

from zope.component import adapts, queryMultiAdapter
from zope.interface import Interface, implements
from zope.interface.common.mapping import IReadMapping


class PublishTraverse(object):
    """Generic PublishTraverse adapter"""

    implements(IPublishTraverse)

    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def publishTraverse(self, request, name):
        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view
        raise KeyError, name


class PublishTraverseMapping(PublishTraverse):
    """Generic PublishTraverse adapter for mappings"""

    adapts(IReadMapping)

    def publishTraverse(self, request, name):
        obj = self.context.get(name, None)
        if obj is not None:
            return obj
        return super(PublishTraverseMapping, self).publishTraverse(request, name)
