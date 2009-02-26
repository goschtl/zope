###############################################################################
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
"""jsmodule directives

$Id$
"""
__docformat__ = 'restructuredtext'
import os
import re

from zope.app.publisher.browser.pagetemplateresource import PageTemplateResourceFactory
from zope.app.publisher.browser.resourcemeta import ResourceFactoryWrapper
from zope.app.publisher.browser.resourcemeta import allowed_names
from zope.component.zcml import handler
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import CheckerPublic, NamesChecker

from z3c.formext import interfaces, jsmodule
from z3c.versionedresource.resource import FileResourceFactory


EXTNamespaceRE = "((?<=Ext.ns\((\"|\'))|(?<=Ext.namespace\((\"|\'))).*(?=(\"|\'))"

def jsmoduleHandler(_context, file, layer=IDefaultBrowserLayer,
                    permission='zope.Public', name=None,
                    namespace=None, dependencies=None):

    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names, permission)

    if dependencies is None:
        dependencies = []

    if namespace is None:
        contents = open(file, 'r').read()
        match = re.search(EXTNamespaceRE, contents)
        if not match:
            raise ConfigurationError(
                "No namespace was specified and no namespace could be extracted")
        namespace = contents[match.start() : match.end()]
    if name is None:
        name = '%s.js' % namespace

    factory = jsmodule.JSModuleResourceFactory(file, checker, name,
                                               namespace, dependencies)

    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = ('registerAdapter', factory, (layer,),
                interfaces.IJSModule, name, _context.info),
        )
