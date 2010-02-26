# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.schema.fieldproperty import FieldProperty
from grokui.base.interfaces import IGrokUIPluginInfo


class BasePluginInfo(grok.GlobalUtility):
    grok.baseclass()
    grok.implements(IGrokUIPluginInfo)

    title = FieldProperty(IGrokUIPluginInfo['title'])
    description = FieldProperty(IGrokUIPluginInfo['description'])
    version = FieldProperty(IGrokUIPluginInfo['version'])
