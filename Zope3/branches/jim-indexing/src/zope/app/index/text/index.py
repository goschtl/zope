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
"""This is a text index

In addition, this implements TTW subscription management.

$Id$
"""
from zope.component import getService
from zope.app.servicenames import HubIds
from zope.app.container.contained import Contained
from zope.index.text.textindexwrapper import TextIndexWrapper

from zope.app.hub.interfaces import \
     IRegistrationHubEvent, IObjectModifiedHubEvent
from zope.app.index.interfaces.text import ISearchableText
from zope.app.index.interfaces.text import IUITextIndex, IUITextCatalogIndex
from zope.interface import implements
from zope.app.index.ifaceindex import InterfaceIndexingSubscriber
from zope.app.catalog.interfaces.index import ICatalogIndex


class TextCatalogIndex(InterfaceIndexingSubscriber, TextIndexWrapper,
                       Contained):
    implements(ICatalogIndex, IUITextCatalogIndex)

    default_interface = ISearchableText
    default_field_name = "getSearchableText"

class TextIndex(TextCatalogIndex):

    implements(IUITextIndex)


