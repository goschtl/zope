##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
from zope import component

from zope.app.intid.interfaces import IIntIdRemovedEvent

from zope.component import getAllUtilitiesRegisteredFor

import interfaces


@component.adapter(IIntIdRemovedEvent)
def o2oIntIdRemoved(event):
    """Subscriber for IIntIdRemovedEvent.

    Remove all relations from the O2ORelation container for the removed object.
    """
    obj = event.object
    for rels in getAllUtilitiesRegisteredFor(
                                    interfaces.IO2OStringTypeRelationships):
        relations = list(rels.findSourceRelationships(obj))
        relations += list(rels.findTargetRelationships(obj))
        for rel in relations:
            rels.remove(rel)

