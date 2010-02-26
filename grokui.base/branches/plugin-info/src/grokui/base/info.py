# -*- coding: utf-8 -*-

import grokcore.viewlet as grok
from grokui.base import IGrokUIPluginInfo, GrokUIView, GrokUILayer, IUIPanel
from megrok.layout import Page
from zope.component import getUtilitiesFor
from zope.location import LocationProxy
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser.absoluteurl import absoluteURL

grok.templatedir('templates')


class BasePluginInfo(grok.GlobalUtility):
    grok.baseclass()
    grok.implements(IGrokUIPluginInfo)

    title = FieldProperty(IGrokUIPluginInfo['title'])
    description = FieldProperty(IGrokUIPluginInfo['description'])
    version = FieldProperty(IGrokUIPluginInfo['version'])


class Plugins(GrokUIView):
    grok.order(50)
    grok.title(u'Information panels')

    def plugins(self):
        plugins = getUtilitiesFor(IGrokUIPluginInfo)
        for name, plugin in plugins:
            located = LocationProxy(plugin, self.context, '++info++%s' % name)
            yield dict(
                url=absoluteURL(located, self.request),
                version=located.version,
                title=located.title,
                description=located.description)


class PluginPage(Page):
    grok.name('index')
    grok.layer(GrokUILayer)
    grok.implements(IUIPanel)
    grok.context(IGrokUIPluginInfo)
