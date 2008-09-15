import grok
import zope.interface


class SmallELearningDemo(grok.Application, grok.Container):

    pass
        

class Index(grok.View):

    pass


class Master(grok.View):
    """A view class provides page template macro."""

    grok.context(zope.interface.Interface)
