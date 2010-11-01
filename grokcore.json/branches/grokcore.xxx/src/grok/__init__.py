##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Grok
"""

from grokcore.component import *
from grokcore.security import *
from grokcore.view import *
from grokcore.formlib import *

from zope.event import notify
from zope.app.component.hooks import getSite
from zope.lifecycleevent import (
    IObjectCreatedEvent, ObjectCreatedEvent,
    IObjectModifiedEvent, ObjectModifiedEvent,
    IObjectCopiedEvent, ObjectCopiedEvent)

from zope.app.container.contained import (
    IObjectAddedEvent, ObjectAddedEvent,
    IObjectMovedEvent, ObjectMovedEvent,
    IObjectRemovedEvent, ObjectRemovedEvent,
    IContainerModifiedEvent, ContainerModifiedEvent)

from martian import ClassGrokker, InstanceGrokker, GlobalGrokker
from grokcore.component import Adapter, MultiAdapter, GlobalUtility
from grok.components import Model, View
from grok.components import XMLRPC, REST, JSON
from grok.components import Traverser
from grok.components import Container, OrderedContainer
from grok.components import Site, LocalUtility, Annotation
from grok.components import Application
from grok.components import Indexes
from grok.components import Role
from grok.components import RESTProtocol, IRESTLayer
from grok.interfaces import IRESTSkinType
from grok.components import ViewletManager, Viewlet
from grok.directive import (
    local_utility, permissions, site,
    traversable, order, viewletmanager)

# BBB These two functions are meant for test fixtures and should be
# imported from grok.testing, not from grok.
from grok.testing import grok, grok_component


# Our __init__ provides the grok API directly so using 'import grok' is enough.
from grok.interfaces import IGrokAPI
from zope.interface import moduleProvides
moduleProvides(IGrokAPI)
__all__ = list(IGrokAPI)
