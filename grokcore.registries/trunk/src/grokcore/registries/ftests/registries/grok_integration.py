"""
 >>> root = getRootFolder()
 >>> create_application(MyApplication, root, 'app')
 <grokcore.registries.ftests.registries.grok_integration.MyApplication ...>

 >>> from zope.component import getUtility
 >>> from grokcore.registries.tests.registries.interfaces import IExample

 >>> getUtility(IExample, name=u'global')
 <grokcore.registries.tests.registries.global.MyExample object at ...>

 >>> getUtility(IExample, name=u'local')
 Traceback (most recent call last):
 ...
 ComponentLookupError: (<InterfaceClass grokcore.registries.tests.registries.interfaces.IExample>, u'local')

 >>> specialRegistry.getUtility(IExample, name=u'local')
 <grokcore.registries.tests.registries.local.MyExample object at ...>

 >>> app = root['app']
 >>> from zope.component.hooks import setSite
 >>> setSite(root['app'])

 >>> getUtility(IExample, name=u'local')
 <grokcore.registries.tests.registries.local.MyExample object at ...>

 >>> setSite()

"""

from grokcore.site import Application
from grokcore.site.util import create_application
from grokcore.registries.ftests.registries.basic import specialRegistry


class MyApplication(Application):

    def getSiteManager(self):
        current = super(MyApplication, self).getSiteManager()
        current.__bases__ += (specialRegistry,)
        return current