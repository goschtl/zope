##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
import grok
import zope.interface
import grokcore.layout
import fanstatic

lib = fanstatic.Library('grokcore.resource.tests', 'resources')

css_a = fanstatic.Resource(lib, 'a.css')
css_b = fanstatic.Resource(lib, 'b.css')
css_c = fanstatic.Resource(lib, 'c.css')
css_d = fanstatic.Resource(lib, 'd.css')

grok.templatedir('templates')

class IMySuperIface(zope.interface.Interface):
    pass

class MyView(grok.View):
    grok.context(zope.interface.Interface)
    grokcore.resource.resources(css_a)
    grok.template('index')

class DocTestView(grok.View):
    grok.context(zope.interface.Interface)
    grokcore.resource.resources(css_a, css_b)
    grok.template('index')
    grok.name('doctest')

class ViewWithOwnResource(MyView):
    grokcore.resource.resources(css_b)

class ViewWithMultipleResources(grok.View):
    grok.context(zope.interface.Interface)
    grokcore.resource.resources(css_c, css_b)
    grok.template('index')

class ViewWithMultipleResourceCalls(grok.View):
    grok.context(zope.interface.Interface)
    grokcore.resource.resources(css_c, css_b)
    grokcore.resource.resources(css_a)
    grok.template('index')

class ViewWithResourceInUpdate(grok.View):
    grok.context(zope.interface.Interface)
    grokcore.resource.resources(css_a)
    grok.template('index')

    def update(self):
        css_d.need()

class MySuperView(grok.View):
    grok.context(zope.interface.Interface)
    zope.interface.implements(IMySuperIface)
    grok.template('index')

class MySuperViewWithResource(grok.View):
    grok.context(zope.interface.Interface)
    zope.interface.implements(IMySuperIface)
    grokcore.resource.resources(css_a)
    grok.template('index')

# Layout.

class MyLayout(grokcore.layout.Layout):
    grok.context(zope.interface.Interface)
    grok.template('layout')
    grokcore.resource.resources(css_a)

class MyPage(grokcore.layout.Page):
    grok.template('page')
    grok.context(zope.interface.Interface)
    grokcore.resource.resources(css_b)

# Viewlet.
class ViewWithViewletManager(grok.View):
    grok.context(zope.interface.Interface)
    grok.template('viewletmgr')

class MyViewletManager(grok.ViewletManager):
    grok.name('foo')
    grok.view(ViewWithViewletManager)
    grok.context(zope.interface.Interface)

class ViewletA(grok.Viewlet):
    grok.viewletmanager(MyViewletManager)
    grokcore.resource.resources(css_a)
    grok.context(zope.interface.Interface)

    def render(self):
        return u'aaa'

class ViewletC(grok.Viewlet):
    grok.viewletmanager(MyViewletManager)
    grokcore.resource.resources(css_c)
    grok.context(zope.interface.Interface)

    def render(self):
        return u'ccc'

# ContentProvider.
class ViewWithContentProvider(grok.View):
    grok.context(zope.interface.Interface)
    grok.template('contentprovider')

class MyContentProvider(grok.ContentProvider):
    grok.name('bar')
    grok.view(ViewWithContentProvider)
    grokcore.resource.resources(css_b)
    grok.context(zope.interface.Interface)

    def render(self):
        return u'bar'
