from zope import component
from zope import event

from zope.security.proxy import removeSecurityProxy
from zope.app.component.interfaces import ISite
from zope.lifecycleevent import ObjectCreatedEvent

from z3c import configurator

from lovely.viewcache.interfaces import IViewCache
from lovely.viewcache.ram import ViewCache as RAMViewCache
from lovely.viewcache.zodb import ViewCache as ZODBViewCache


class RAMViewCacheConfigurator(configurator.ConfigurationPluginBase):
    component.adapts(ISite)

    def __call__(self, data):
        sm = removeSecurityProxy(self.context.getSiteManager())
        default = sm['default']

        if 'view-cache-RAM' not in default:
            util = RAMViewCache()
            event.notify(ObjectCreatedEvent(util))
            default['view-cache-RAM'] = util
            sm.registerUtility(util, IViewCache)


class ZODBViewCacheConfigurator(configurator.ConfigurationPluginBase):
    component.adapts(ISite)

    def __call__(self, data):
        sm = removeSecurityProxy(self.context.getSiteManager())
        default = sm['default']

        if 'view-cache-ZODB' not in default:
            util = ZODBViewCache()
            event.notify(ObjectCreatedEvent(util))
            default['view-cache-ZODB'] = util
            sm.registerUtility(util, IViewCache)

