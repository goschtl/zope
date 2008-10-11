from OFS.interfaces import IItem

from zope.interface import implements

import grokcore.component

from plone.clids.interfaces import IUniqueId
from plone.clids.interfaces import IResolver
from plone.clids.interfaces import IResolvable

from Zope2 import App


class Resolver(object):
    implements(IResolver)

    def resolve(self, data):
        return App().restrictedTraverse('/'.join(data))

resolver = Resolver()


class Resolvable(grokcore.component.Adapter):
    grokcore.component.context(IItem)
    grokcore.component.implements(IResolvable)

    @property
    def data(self):
        return self.context.getPhysicalPath()

    @property
    def resolver(self):
        return resolver


class UniqueForSimpleItem(grokcore.component.Adapter):
    grokcore.component.context(IItem)
    grokcore.component.implements(IUniqueId)

    @property
    def id(self):
        return '/'.join(self.context.getPhysicalPath())
