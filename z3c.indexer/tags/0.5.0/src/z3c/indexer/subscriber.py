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

import zope.component
from zope.app.intid.interfaces import IIntIdAddedEvent
from zope.app.intid.interfaces import IIntIdRemovedEvent

from z3c.indexer import interfaces


@zope.component.adapter(IIntIdAddedEvent)
def autoIndexSubscriber(event):
    """Index all objects which get added to the intids utility."""
    adapters = zope.component.getAdapters((event.object,),
        interfaces.IAutoIndexer)
    for name, adapter in adapters:
        adapter.doIndex()



@zope.component.adapter(IIntIdRemovedEvent)
def autoUnindexSubscriber(event):
    """Unindex all objects which get added to the intids utility."""
    adapters = zope.component.getAdapters((event.object,),
        interfaces.IAutoIndexer)
    for name, adapter in adapters:
        adapter.doUnIndex()