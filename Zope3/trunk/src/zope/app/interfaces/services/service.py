##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interfaces to support service managers.

$Id: service.py,v 1.10 2003/03/18 21:02:22 jim Exp $
"""
__metaclass__ = type

from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.component.interfacefield import InterfaceField
from zope.schema import BytesLine
from zope.component.interfaces import IPresentation
from zope.app.interfaces.container import IContainer
from zope.app.security.permission import PermissionField
from zope.interface import Interface, Attribute
from zope.component.interfaces import IServiceService
from zope.app.interfaces.services import configuration


class ILocalService(configuration.IUseConfigurable):
    """A local service isn't a local service if it doesn't implement this.

    The contract of a local service includes collaboration with
    services above it.  A local service should also implement
    IUseConfigurable (which implies that it is adaptable to
    IUseConfiguration).  Implementing ILocalService implies this.
    """


class ISimpleService(ILocalService, configuration.IAttributeUseConfigurable):
    """Most local services should implement this instead of ILocalService.

    It implies a specific way of implementing IUseConfigurable,
    by subclassing IAttributeUseConfigurable.
    """

class IComponentManager(Interface):

    def queryComponent(type=None, filter=None, all=0):
        """Return all components that match the given type and filter

        The objects are returned a sequence of mapping objects with keys:

        path -- The component path

        component -- The component

        all -- A flag indicating whether all component managers in
               this place should be queried, or just the local one.

        """


class IReadServiceManagerContainer(Interface):

    def getServiceManager():
        """Returns the service manager contained in this object.

        If there isn't a service manager, raise a component lookup.
        """

    def queryServiceManager(default=None):
        """Returns the service manager contained in this object.

        If there isn't a service manager, return the default.
        """

    def hasServiceManager():
        """Query to find out if the component defines a service manager."""

Read = IReadServiceManagerContainer

class IWriteServiceManagerContainer(Interface):

    def setServiceManager(sm):
        """Sets the service manager for this object."""

Write = IWriteServiceManagerContainer

class IServiceManagerContainer(IReadServiceManagerContainer,
                               IWriteServiceManagerContainer):
    pass


class IBindingAware(Interface):

    def bound(name):
        """Inform a service component that it is providing a service

        Called when an immediately-containing service manager binds
        this object to perform the named service.
        """

    def unbound(name):
        """Inform a service component that it is no longer providing a service

        Called when an immediately-containing service manager unbinds
        this object from performing the named service.
        """


class IServiceManager(IServiceService, IComponentManager,
                      configuration.INameComponentConfigurable):
    """Service Managers act as containers for Services.

    If a Service Manager is asked for a service, it checks for those it
    contains before using a context based lookup to find another service
    manager to delegate to.  If no other service manager is found they defer
    to the ComponentArchitecture ServiceManager which contains file based
    services.
    """

class IServiceConfiguration(configuration.INamedComponentConfiguration):
    """Service Configuration

    Service configurations are dependent on the components that they
    configure. They register themselves as component dependents.

    The name of a service configuration is used to determine the service
    type.
    """

class IViewPackageInfo(Interface):

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being viewed",
        required = True,
        )

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the view",
        required = True,
        )

    layer = BytesLine(
        title = u"Layer",
        description = u"The skin layer the view is registered for",
        required = False,
        min_length = 1,
        default = "default",
        )

    permission = PermissionField(
        title=u"Permission",
        description=u"The permission required to use the view",
        required = True,
        )

class IViewPackage(IViewPackageInfo,  IContainer):
    """Sub-packages that contain templates that are registered as views
    """
