##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Remote object traverser.

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.interface import declarations
from zope.proxy import getProxiedObject, removeAllProxies
from zope.proxy.decorator import DecoratorSpecificationDescriptor
from zope.publisher.interfaces.browser import IBrowserPublisher, IBrowserRequest

from z3c.mountpoint import interfaces

class RemoteLocationProxyDecoratorSpecificationDescriptor(
    DecoratorSpecificationDescriptor):

    def __get__(self, inst, cls=None):
        if inst is None:
            return declarations.getObjectSpecification(cls)
        else:
            provided = zope.interface.providedBy(getProxiedObject(inst))

            # Use type rather than __class__ because inst is a proxy and
            # will return the proxied object's class.
            cls = type(inst)
            # Create a special version of Provides, which forces the remote
            # location proxy to the front, so that a special traverser can be
            # enforced.
            return declarations.Provides(
                cls, interfaces.IRemoteLocationProxy, provided)


class RemoteLocationProxy(zope.location.LocationProxy):
    """A location proxy for remote objects."""
    __providedBy__ = RemoteLocationProxyDecoratorSpecificationDescriptor()


class RemoteLocationProxyTraverser(object):
    zope.component.adapts(interfaces.IRemoteLocationProxy, IBrowserRequest)
    zope.interface.implements(IBrowserPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def browserDefault(self, request):
        ob = self.context
        view_name = zapi.getDefaultViewName(ob, request)
        return ob, (view_name,)

    def publishTraverse(self, request, name):
        pureContext = removeAllProxies(self.context)
        traverser = zope.component.getMultiAdapter(
            (pureContext, self.request), IBrowserPublisher)
        result = traverser.publishTraverse(request, name)
        # Only remove the security proxy from the context.
        return RemoteLocationProxy(result, getProxiedObject(self.context), name)
