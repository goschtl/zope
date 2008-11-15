#############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

import martian
import five.grok
import grokcore.security
import grokcore.view
import grokcore.component

from zope import interface, component
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from five.grok import components
from grokcore.view.meta.directoryresource import _get_resource_path
from martian.error import GrokError

from Products.Five.security import protectClass, protectName
from Globals import InitializeClass as initializeClass

import os.path

class ViewSecurityGrokker(martian.ClassGrokker):
    martian.component(five.grok.View)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        if permission is None:
            permission = 'zope.Public'

        config.action(
            discriminator = ('five:protectClass', factory),
            callable = protectClass,
            args = (factory, permission)
            )

        # Protect the class
        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,)
            )

        return True


def _register_resource(config, resource_path, name, layer):
    resource_factory = components.ZopeTwoDirectoryResourceFactory(
        name, resource_path)
    adapts = (layer,)
    provides = interface.Interface

    config.action(
        discriminator=('adapter', adapts, provides, name),
        callable=component.provideAdapter,
        args=(resource_factory, adapts, provides, name),
        )
    return True


class DirectoryResourceGrokker(martian.ClassGrokker):
    martian.component(components.ZopeTwoDirectoryResource)

    martian.directive(grokcore.view.name, default=None)
    martian.directive(grokcore.view.path)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the directory resource
        # class so that it can look up the actual directory.
        factory.module_info = module_info
        return super(DirectoryResourceGrokker, self).grok(
            name, factory, module_info, **kw)

    def execute(self, factory, config, name, path, layer, **kw):
        resource_path = _get_resource_path(factory.module_info, path)
        name = name or factory.module_info.dotted_name
        return _register_resource(config, resource_path, name, layer)


class StaticResourcesGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        # we're only interested in static resources if this module
        # happens to be a package
        if not module_info.isPackage():
            return False
        resource_path = _get_resource_path(module_info, 'static')
        name = module_info.dotted_name
        layer = IDefaultBrowserLayer
        return _register_resource(config, resource_path, name, layer)


class ViewletSecurityGrokker(martian.ClassGrokker):
    martian.component(five.grok.Viewlet)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        if permission is None:
            permission = 'zope.Public'

        attributes = ['update', 'render',]
        config.action(
            discriminator = ('five:protectClass', factory),
            callable = protectClass,
            args = (factory, permission)
            )
        for attribute in attributes:
            config.action(
                discriminator = ('five:protectName', factory, attribute),
                callable = protectName,
                args = (factory, attribute, permission)
                )

        # Protect the class
        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,)
            )

        return True
