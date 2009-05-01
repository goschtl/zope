from zope.testing.cleanup import addCleanUp
from zope import component
from zope.component import registry

# a very simple implementation of setSite and getSite so we don't have
# to rely on zope.app.component just for our tests
_site = None

class DummySite(object):
    def __init__(self, id):
        self.id = id
        self._sm = SiteManager()
        
    def getSiteManager(self):
        return self._sm

class SiteManager(registry.Components):
    def __init__(self):
        super(SiteManager, self).__init__()
        self.__bases__ = (component.getGlobalSiteManager(),)

def setSite(site=None):
    global _site
    _site = site

def getSite():
    return _site

def adapter_hook(interface, object, name='', default=None):
    try:
        return getSiteManager().adapters.adapter_hook(
            interface, object, name, default)
    except component.interfaces.ComponentLookupError:
        return default

def getSiteManager(context=None):
    if _site is not None:
        return _site.getSiteManager()
    return component.getGlobalSiteManager()

def setHooks():
    component.adapter_hook.sethook(adapter_hook)
    component.getSiteManager.sethook(getSiteManager)

def resetHooks():
    component.adapter_hook.reset()
    component.getSiteManager.reset()

# make sure hooks get cleaned up after tests are run
addCleanUp(resetHooks)
