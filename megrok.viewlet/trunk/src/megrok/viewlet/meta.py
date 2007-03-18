##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Interfaces
"""
from zope import component
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewlet, IViewletManager
from zope.viewlet.manager import ViewletManagerBase
from zope.security.checker import NamesChecker, defineChecker

import grok

class ViewletManager(ViewletManagerBase, grok.Model):
    template = None
        
class ViewletManagerGrokker(grok.ClassGrokker):
    component_class = ViewletManager

    def register(self, context, name, factory, module_info, templates):
        provides = grok.util.class_annotation(factory, 'grok.provides', None)
        name = grok.util.class_annotation(factory, 'grok.name', name)
        component.provideAdapter(factory,
                                 adapts=(None, # TODO: Make configurable
                                         IDefaultBrowserLayer, # TODO: Make configurable
                                         IBrowserView),
                                 provides=provides,
                                 name=name)
        
class Viewlet(grok.Model):

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        
    def update(self):
        pass
        
class ViewletGrokker(grok.ClassGrokker):
    component_class = Viewlet

    def register(self, context, name, factory, module_info, templates):
        # Try to set up permissions (copied from the View grokker)
        permissions = grok.util.class_annotation(factory, 'grok.require', [])
        if not permissions:
            checker = NamesChecker(['render'])
        elif len(permissions) > 1:
            raise GrokError('grok.require was called multiple times in viewlet '
                            '%r. It may only be called once.' % factory,
                            factory)
        elif permissions[0] == 'zope.Public':
            checker = NamesChecker(['render'])
        else:
            perm = permissions[0]
            if component.queryUtility(IPermission, name=perm) is None:
                raise GrokError('Undefined permission %r in view %r. Use '
                                'grok.define_permission first.'
                                % (perm, factory), factory)
            checker = NamesChecker(['render'], permissions[0])

        defineChecker(factory, checker)
        
        manager = factory.viewlet_manager
        component.provideAdapter(factory,
                                 adapts=(None, # TODO: Make configurable
                                         IDefaultBrowserLayer, # TODO: Make configurable
                                         IBrowserView, 
                                         manager),
                                 provides=IViewlet,
                                 name=name)
        