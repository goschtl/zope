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
"""This is a field index which can be subscribed to an event service.

Events related to object creation and deletion are translated into
index_doc() and unindex_doc() calls.

In addition, this implements TTW subscription management.

$Id$
"""
from zope.component import getService
from zope.app.servicenames import HubIds
from zope.index.field.index import FieldIndex as FieldIndexWrapper
from zope.interface import implements
from zope.app.container.contained import Contained
from zope.app.hub.interfaces import IObjectModifiedHubEvent
from zope.app.hub.interfaces import IRegistrationHubEvent
from zope.app.index.interfaces.field import IUIFieldIndex, IUIFieldCatalogIndex
from zope.app.catalog.interfaces.index import ICatalogIndex
from zope.app.index.ifaceindex import InterfaceIndexingSubscriber

class FieldCatalogIndex(InterfaceIndexingSubscriber, FieldIndexWrapper,
                        Contained):
    implements(ICatalogIndex, IUIFieldCatalogIndex)

class FieldIndex(FieldCatalogIndex):

    implements(IUIFieldIndex)

