##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Simple Pagelet Implementation

$Id$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.contentprovider
import zope.interface
import zope.security.proxy
import zope.viewlet
from persistent.dict import PersistentDict
from zope.app import annotation
from zope.app import container
from zope.app.component import hooks

PAGELET_MANAGER_KEY = 'zope.webdev.pageletmanagaer'


class IPagelet(zope.viewlet.interfaces.IViewlet):
    """A viewlet that knows about its state."""

    state = zope.interface.Attribute('State of the pagelet')


class IPageletManager(zope.viewlet.interfaces.IViewletManager,
                      container.interfaces.ISimpleReadContainer):
    """A viewlet manager that can be traversed and store the state of its
    viewlets."""

    def getState(name):
        """Get the state object for the named pagelet."""


class PageletManagerBase(object):
    """A class that must be used as a base class in combination with an object
    implementing ``IViewletManager``."""

    def getState(self, name):
        """See IPageletManager."""
        site = hooks.getSite()
        # get the pagelet manager annotations; they are stored in the site.
        ann = annotation.interfaces.IAnnotations(site)
        if not ann.has_key(PAGELET_MANAGER_KEY):
            ann[PAGELET_MANAGER_KEY] = PersistentDict()
        # get the state object.
        states = ann[PAGELET_MANAGER_KEY]
        if not states.has_key(name):
            states[name] = PersistentDict()

        return states[name]


class pageletsNamespace(object):
    """Used to traverse to a pagelet manager."""
    def __init__(self, ob, request=None):
        if request is None:
            # the object *must* be a view
            request = ob.request
        self.view = ob
        naked = zope.security.proxy.removeSecurityProxy(ob)
        self.context = naked.context
        self.request = request

    def traverse(self, name, ignore):
        if not name:
            raise ValueError('A pagelet manager name is required.')

        manager = zope.component.queryMultiAdapter(
            (self.context, self.request, self.view), IPageletManager, name)

        # Provide a useful error message, if the manager was not found.
        if manager is None:
            raise \
              zope.contentprovider.interfaces.ContentProviderLookupError(name)

        return manager
