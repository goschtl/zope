import grok
from zope.interface import alsoProvides
from zope.publisher.publish import mapply
from zope.security.proxy import removeSecurityProxy
from kss.core import KSSView
try:
    from grok.interfaces import IGrokSecurityView
except ImportError:
    # Older Grok versions (< 1.0) do not provide this interface. We
    # use a dummy instead.
    from megrok.kss.interfaces import (
        IGrokSecurityViewPlaceholder as IGrokSecurityView)

class KSS(KSSView, grok.View):
    """This is the default KSS action class that binds to a content object.

    We also derive from `grok.View` to let our views pass by the Grok
    security checks in Grok versions < 1.0. We also get some nice
    bonus features by that.

    In other words: the Grok publication process (with grok < 1.0)
    requires this view to be also an instance of
    `grok.View`. Otherwise we would have no access to
    self.context.context.
    """
    grok.implements(IGrokSecurityView)
    grok.baseclass() # This is a baseclass. Create your own KSS views.
    
    def __init__(self, context, request):
        self.view = context
        super(KSS, self).__init__(context, request)
        if not IGrokSecurityView.providedBy(context):
            # Waah, we have to remove security, because otherwise all
            # context views had to provide ISecurityView themselves.
            #
            # If all grok.View instances would provide `IGrokSecurityView`,
            # this would not be needed.
            self.view = removeSecurityProxy(self.view)
            alsoProvides(self.view, IGrokSecurityView)
        self.context = self.view.context

    def __call__(self):
        view_name = self.__view_name__
        method = getattr(self, view_name)
        method_result = mapply(method, (), self.request)
        return self.render()
