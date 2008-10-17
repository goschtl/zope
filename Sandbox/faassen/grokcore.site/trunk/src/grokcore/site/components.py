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
"""Grok components"""

import persistent
import simplejson

import zope.location
from zope import component
from zope import interface
from zope.securitypolicy.role import Role
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.publish import mapply
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.app.publisher.browser import getDefaultViewName
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IReadContainer, IObjectAddedEvent
from zope.app.container.interfaces import IOrderedContainer
from zope.app.container.contained import notifyContainerModified
from persistent.list import PersistentList
from zope.app.component.site import SiteManagerContainer
from zope.app.component.site import LocalSiteManager

from zope.viewlet.manager import ViewletManagerBase
from zope.viewlet.viewlet import ViewletBase

import grok
import z3c.flashmessage.interfaces
import martian.util

import grokcore.view
import grokcore.formlib
from grok import interfaces, util


class Site(SiteManagerContainer):
    pass

@component.adapter(Site, IObjectAddedEvent)
def addSiteHandler(site, event):
    sitemanager = LocalSiteManager(site)
    # LocalSiteManager creates the 'default' folder in its __init__.
    # It's not needed anymore in new versions of Zope 3, therefore we
    # remove it
    del sitemanager['default']
    site.setSiteManager(sitemanager)

class LocalUtility(Model):
    pass
