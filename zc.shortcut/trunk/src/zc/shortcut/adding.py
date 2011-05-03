##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""shortcut adding

$Id: adding.py 1876 2005-05-31 22:23:43Z gary $
"""
from zope import interface, component
from zope.event import notify
import zope.security.checker
from zope.security.proxy import removeSecurityProxy
from zope.component.interfaces import IFactory
from zope.app.component.hooks import getSite
import zope.app.container.browser.adding
from zope.app.container.constraints import checkObject
from zope.lifecycleevent import ObjectCreatedEvent
from zope.exceptions.interfaces import UserError
from zope.location.interfaces import ILocation
from zope.location import LocationProxy

from zc.shortcut import Shortcut, traversedURL, interfaces

class Adding(zope.app.container.browser.adding.Adding):
    interface.implements(interfaces.IAdding)

    def action(self, type_name='', id=''):
        # copied from zope.app.container.browser.adding.Adding;
        # only change is that we use traversedURL, not absoluteURL
        if not type_name:
            raise UserError(_(u"You must select the type of object to add."))
        if type_name.startswith('@@'):
            type_name = type_name[2:]
        if '/' in type_name:
            view_name = type_name.split('/', 1)[0]
        else:
            view_name = type_name
        if component.queryMultiAdapter((self, self.request),
                                  name=view_name) is not None:
            url = "%s/@@+/%s=%s" % (
                traversedURL(self.context, self.request), type_name, id)
            self.request.response.redirect(url)
            return
        if not self.contentName:
            self.contentName = id
        # TODO: If the factory wrapped by LocationProxy is already a Proxy,
        #       then ProxyFactory does not do the right thing and the
        #       original's checker info gets lost. No factory that was
        #       registered via ZCML and was used via addMenuItem worked
        #       here. (SR)
        factory = component.getUtility(IFactory, type_name)
        if not type(factory) is zope.security.checker.Proxy:
            factory = LocationProxy(factory, self, type_name)
            factory = zope.security.checker.ProxyFactory(factory)
        content = factory()
        # Can't store security proxies.
        # Note that it is important to do this here, rather than
        # in add, otherwise, someone might be able to trick add
        # into unproxying an existing object,
        content = removeSecurityProxy(content)
        notify(ObjectCreatedEvent(content))
        self.add(content)
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        """See zope.app.container.interfaces.IAdding"""
        content = self.context[self.contentName] # this will be a shortcut
        # when item was added to a repository
        nextURL = component.queryMultiAdapter(
            (self, content, self.context), name=interfaces.NEXT_URL_NAME)
        if nextURL is None:
            nextURL = (
                traversedURL(self.context, self.request) + '/@@contents.html')
        return nextURL

