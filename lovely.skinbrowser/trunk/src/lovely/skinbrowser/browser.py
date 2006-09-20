##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Browser Views for Skin Browser

$Id$
"""
__docformat__ = 'restructuredtext'
import inspect
import zope.interface
from zope.app.apidoc import component, interface, presentation, utilities
from zope.app.apidoc.ifacemodule.browser import InterfaceDetails
from zope.configuration.xmlconfig import ParserInfo
from zope.security import proxy


class TemplateDetails(object):
    """View class for a Template."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def macro(self):
        return self.context.macro

    @property
    def filename(self):
        file = self.context.filename
        return {'file': utilities.relativizePath(file),
                'url': utilities.truncateSysPath(file).replace('\\', '/')}

    @property
    def contentType(self):
        return self.context.contentType

    def fileInfo(self):
        """Get the file where the directive was declared."""
        info = proxy.removeSecurityProxy(self.context.reg).info
        if proxy.isinstance(info, ParserInfo):
            return component.getParserInfoInfoDictionary(info)
        return None

    def permission(self):
        """Get the permission to access the view."""
        reg = proxy.removeSecurityProxy(self.context.reg)
        perms = utilities.getPermissionIds('publishTraverse', klass=reg.factory)
        return perms['read_perm']

    def validationMessages(self):
        return [
            zope.component.getMultiAdapter(
                (message, self.request), name='listitem')
            for message in self.context.validate()]


class ViewDetails(object):
    """View class for a View."""

    # Attributes that are always available can be ignored here.
    excludeAttrs = ('__parent__', '__name__', 'context', 'request',
                    'browserDefault', 'publishTraverse',
                    'update', 'render', '__call__')

    def viewTemplate(self):
        if self.context.template:
            return TemplateDetails(self.context.template, self.request)

    def fileInfo(self):
        """Get the file where the directive was declared."""
        info = proxy.removeSecurityProxy(self.context.reg).info
        if proxy.isinstance(info, ParserInfo):
            return component.getParserInfoInfoDictionary(info)
        return None

    def factory(self):
        """Get factory info"""
        reg = proxy.removeSecurityProxy(self.context.reg)
        return presentation.getViewFactoryData(reg.factory)

    def permission(self):
        """Get the permission to access the view."""
        reg = proxy.removeSecurityProxy(self.context.reg)
        perms = utilities.getPermissionIds('publishTraverse', klass=reg.factory)
        return perms['read_perm']

    def doc(self):
        reg = proxy.removeSecurityProxy(self.context.reg)
        factory = component.getRealFactory(reg.factory)
        if factory.__doc__:
            return utilities.renderText(
                factory.__doc__, inspect.getmodule(factory))
        ifaces = tuple(zope.interface.implementedBy(factory).interfaces())
        if ifaces[0].__doc__:
            iface = ifaces[0]
            return utilities.renderText(iface.__doc__, inspect.getmodule(iface))

    @property
    def iface(self):
        reg = proxy.removeSecurityProxy(self.context.reg)
        factory = component.getRealFactory(reg.factory)
        implements = zope.interface.implementedBy(factory)
        return zope.interface.interface.InterfaceClass(
            'ITemporary', bases=tuple(implements.interfaces()))

    def getAttributes(self):
        """Return a list of attributes in the order they were specified."""
        return [interface.getAttributeInfoDictionary(attr)
                for name, attr in interface.getAttributes(self.iface)
                if name not in self.excludeAttrs]

    def getMethods(self):
        """Return a list of methods in the order they were specified."""
        return [interface.getMethodInfoDictionary(method)
                for name, method in interface.getMethods(self.iface)
                if name not in self.excludeAttrs]

    def getFields(self):
        r"""Return a list of fields in required + alphabetical order.

        The required attributes are listed first, then the optional
        attributes."""
        # Make sure that the required fields are shown first
        sorter = lambda x, y: cmp((not x[1].required, x[0].lower()),
                                  (not y[1].required, y[0].lower()))
        return [
            interface.getFieldInfoDictionary(field)
            for name, field in interface.getFieldsInOrder(self.iface, sorter)
            if name not in self.excludeAttrs]
