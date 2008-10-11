from OFS.interfaces import IItem

from zope.interface import implements

import grokcore.component

from plone.clids.interfaces import IUniqueId
from plone.clids.interfaces import IResolver
from plone.clids.interfaces import IResolvable


class Resolver(object):
    implements(IResolver)

    def __init__(self, context):
        self.context = context

    def resolve(self, data):
        app = self.context.getPhysicalRoot()
        return app.unrestrictedTraverse(data)


class Resolvable(grokcore.component.Adapter):
    grokcore.component.context(IItem)
    grokcore.component.implements(IResolvable)

    @property
    def data(self):
        return self.context.getPhysicalPath()

    @property
    def resolver(self):
        return Resolver


class UniqueForSimpleItem(grokcore.component.Adapter):
    grokcore.component.context(IItem)
    grokcore.component.implements(IUniqueId)

    @property
    def id(self):
        return '/'.join(self.context.getPhysicalPath())
