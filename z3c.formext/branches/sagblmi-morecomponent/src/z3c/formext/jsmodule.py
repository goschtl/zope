##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Versioned Resources Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import cjson
from zope.publisher.interfaces import NotFound
from zope.app.publisher.browser import resource, resources
from zope.app.publisher.browser import directoryresource
from zope.app.publisher.browser import fileresource
from zope.app.publisher.browser import pagetemplateresource
from zope.viewlet.viewlet import ViewletBase
from zope.viewlet.viewlet import JavaScriptViewlet
from z3c.versionedresource import interfaces
from z3c.versionedresource.resource import FileResource

from z3c.formext import interfaces

class JSModuleResourceFactory(fileresource.FileResourceFactory):
    resourceClass = FileResource

    def __init__(self, path, checker, name, namespace, dependencies):
        super(JSModuleResourceFactory, self).__init__(path, checker, name)
        self.namespace = namespace
        self.dependencies = dependencies

    def __call__(self, request):
        resource = super(JSModuleResourceFactory, self).__call__(request)
        resource.namespace = self.namespace
        resource.dependencies = self.dependencies
        return resource


class JSModulesViewlet(ViewletBase):

    def render(self):
        result = {}
        for name, resource in zope.component.getAdapters((self.request,),
                                                         interfaces.IJSModule):
            result[resource.namespace] = {
                "name":resource.namespace,
                "scripts":[resource()],
                "requires":resource.dependencies,
                "url":resource(),
                "dependencies":resource.dependencies}
        return ('<script type="text/javascript">'
                'Ext.ns("z3c.formext"); '
                'z3c.formext.JS_MODULES = %s;'
                'for (pkg in z3c.formext.JS_MODULES){'
                'z3c.formext.ModuleLoader.register(z3c.formext.JS_MODULES[pkg]);'
                '}'
                '</script>' % cjson.encode(result))

LoaderViewlet = JavaScriptViewlet('z3c.formext.loader.js')
