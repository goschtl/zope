from zope.publisher.publish import mapply
from kss.core import KSSView


class KSSActions(KSSView):
    """This is the default KSSActions class that binds to a content object.
    """

    def __call__(self):
        view_name = self.__view_name__
        method = getattr(self, view_name)
        method_result = mapply(method, (), self.request)
        return self.render()


class KSSActionsForView(KSSView):
    """This KSSActions class is bound to a view class.
    """
    
    def __init__(self, context, request):
        self.view = context
        super(KSSActionsForView, self).__init__(context, request)
        self.context = context.context

    def __call__(self):
        view_name = self.__view_name__
        method = getattr(self, view_name)
        method_result = mapply(method, (), self.request)
        return self.render()
