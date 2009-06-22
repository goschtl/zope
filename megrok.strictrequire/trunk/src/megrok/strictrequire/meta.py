import martian
import grok

class SecurityError(grok.GrokError):
    pass


_require_marker = object()


class CheckRequireGrokker(martian.ClassGrokker):
    """Ensure every grok.View has a grok.require directive"""
    martian.component(grok.View)
    martian.directive(grok.require, default=_require_marker)

    def execute(self, factory, config, require, **kw):
        if require is _require_marker:
            raise SecurityError(
                'megrok.strictrequire requires %r to use the grok.require '
                'directive!' % factory, factory)
        return True


class CheckRequireGrokkerViewlet(CheckRequireGrokker):
    """Ensure every grok.Viewlet has a grok.require directive"""
    martian.component(grok.Viewlet)


class CheckRequireGrokkerViewletmanager(CheckRequireGrokker):
    """Ensure every grok.ViewletManager has a grok.require directive"""
    martian.component(grok.ViewletManager)


class CheckRequireRESTGrokker(martian.MethodGrokker):
    """Ensure every grok.REST has a grok.require directive"""
    martian.component(grok.REST)
    martian.directive(grok.require, default=_require_marker)

    def execute(self, factory, method, config, require, **kw):
        if require is _require_marker:
            raise SecurityError(
                'megrok.strictrequire requires %r to use the grok.require '
                'directive on the method: %s!' % (factory, method), factory)
        return True


class CheckRequireXMLPRCGrokker(CheckRequireRESTGrokker):
    martian.component(grok.XMLRPC)


class CheckRequireJSONGrokker(CheckRequireRESTGrokker):
    martian.component(grok.JSON)
