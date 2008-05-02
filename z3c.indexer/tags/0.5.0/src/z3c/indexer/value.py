##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
from z3c.indexer import interfaces


class IIndexValue(object):
    """Index value adapter""" 

    zope.interface.implements(interfaces.IIndexValue)

    def __init__self(self, context, index):
        self.context = context
        self.index = index

    @property
    def value(self):
        raise NotImplementedError('Sub class must implement value attribute')
