"""Grokkers for megrok.feeds components."""
import grok
import martian
from zope import interface, component
from megrok.feeds import components
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from grok import util

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

class AtomFeedGrokker(martian.ClassGrokker):
    martian.component(components.AtomFeed)
    martian.directive(grok.layer, default=IDefaultBrowserLayer)
    martian.directive(grok.name, get_default=default_view_name)
    martian.directive(grok.require, name='permission')

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(AtomFeedGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, layer, name, permission, **kw):
        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if grok.require.bind().get(method) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (components.IFeedable, layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, name),
            )

        config.action(
            discriminator=('protectName', factory, '__call__'),
            callable=util.make_checker,
            args=(factory, factory, permission),
            )

        return True
