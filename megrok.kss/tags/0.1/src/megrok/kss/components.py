from zope.publisher.publish import mapply

from kss.core import KSSView

class KSSActions(KSSView):
   
    def __call__(self):
        view_name = self.__view_name__
        method = getattr(self, view_name)
        method_result = mapply(method, (), self.request)
        return self.render()

