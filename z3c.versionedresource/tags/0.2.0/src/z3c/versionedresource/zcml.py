##############################################################################
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
"""Resource Directives

$Id$
"""
__docformat__ = 'restructuredtext'
import os
from zope.app.publisher.browser.resourcemeta import ResourceFactoryWrapper
from zope.app.publisher.browser.resourcemeta import allowed_names
from zope.app.publisher.browser.pagetemplateresource import \
     PageTemplateResourceFactory
from zope.component.zcml import handler
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import CheckerPublic, NamesChecker

from z3c.versionedresource import interfaces
from z3c.versionedresource.resource import DirectoryResourceFactory
from z3c.versionedresource.resource import FileResourceFactory
from z3c.versionedresource.resource import ImageResourceFactory


def resource(_context, name, layer=IDefaultBrowserLayer,
             permission='zope.Public', factory=None,
             file=None, image=None, template=None):

    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names, permission)

    if (factory and (file or image or template)) or \
       (file and (factory or image or template)) or \
       (image and (factory or file or template)) or \
       (template and (factory or file or image)):
        raise ConfigurationError(
            "Must use exactly one of factory or file or image or template"
            " attributes for resource directives"
            )

    if factory is not None:
        factory = ResourceFactoryWrapper(factory, checker, name)
    elif file:
        factory = FileResourceFactory(file, checker, name)
    elif image:
        factory = ImageResourceFactory(image, checker, name)
    else:
        factory = PageTemplateResourceFactory(template, checker, name)

    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = ('registerAdapter', factory, (layer,),
                interfaces.IVersionedResource, name, _context.info),
        )


def resourceDirectory(_context, name, directory, layer=IDefaultBrowserLayer,
                      permission='zope.Public'):
    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names + ('__getitem__', 'get'),
                           permission)

    if not os.path.isdir(directory):
        raise ConfigurationError(
            "Directory %s does not exist" % directory
            )

    factory = DirectoryResourceFactory(directory, checker, name)
    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = ('registerAdapter', factory, (layer,),
                interfaces.IVersionedResource, name, _context.info),
        )
