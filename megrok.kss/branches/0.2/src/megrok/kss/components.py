import grok
from zope.publisher.publish import mapply
from kss.core import KSSView

class DummyModel(grok.Model):
    """A dummy model.

    This model is needed to have a context for the `KSS` view
    below. Otherwise grokking would fail. As soon as grok provides
    `IGrokSecurityView` we can get rid of this.
    """
    pass

class KSS(KSSView, grok.View):
    """This is the default KSS action class that binds to a content object.

    We also derive from `grok.View` to let our views pass by the Grok
    security checks. We also get some nice bonus features by that.
    """

    grok.context(DummyModel)
    
    def __init__(self, context, request):
        self.view = context
        super(KSS, self).__init__(context, request)
        self.context = context.context

    def __call__(self):
        view_name = self.__view_name__
        method = getattr(self, view_name)
        method_result = mapply(method, (), self.request)
        return self.render()
