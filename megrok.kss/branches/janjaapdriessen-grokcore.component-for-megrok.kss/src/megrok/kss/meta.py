import martian

import grok
from grok.util import make_checker

from zope import component
from zope import interface
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from megrok.kss.components import KSS


class KSSGrokker(martian.MethodGrokker):
    martian.component(KSS)
    martian.directive(grok.directive.view)
    martian.directive(grok.require, name='permission')

    def execute(self, factory, method, config, view, permission, **kw):

        # Create a new class with a __view_name__ attribute so the
        # KSSServerAction class knows what method to call.
        name = method.__name__
        method_view = type(
            factory.__name__, (factory, BrowserPage),
            {'__view_name__': name})

        adapts = (view, IDefaultBrowserLayer)
        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(method_view, adapts, interface.Interface, name))
        config.action(
            discriminator=('protectName', method_view, '__call__'),
            callable=make_checker,
            args=(factory, method_view, permission))

        return True
