import Acquisition
from AccessControl import getSecurityManager
from zExceptions import Unauthorized

from zope.component import getView

class FiveViewError(Exception):
    pass

class ViewAttribute(Acquisition.Explicit):

    def __init__(self, view_type):
        self._view_type = view_type

    def index_html(self):
        """Default method on view
        """
        # need this info to do security checks, so can't delegate to
        # __getitem__
        obj = self.aq_parent
        view = getView(obj, self._view_type, self.aq_acquire('REQUEST'))
        view = view.__of__(obj)
        method_on_view = getattr(view, 'index_html', None)
        if method_on_view is None:
            raise FiveViewError, "No default view (index_html)"
        security_manager = getSecurityManager()
        if not security_manager.validate(method_on_view, obj, 'index_html',
                                         method_on_view):
            raise Unauthorized
        return method_on_view()

    def __getitem__(self, name):
        """Get correct method on view
        """
        # get the object we are viewing
        obj = self.aq_parent
        # look up the view
        view = getView(obj, self._view_type, self.aq_acquire('REQUEST'))
        # wrap it in the right acquisition context for security
        view = view.__of__(obj)
        # look up method
        method_on_view = getattr(view, name, None)

        if method_on_view is None:
            # we do not accept calling unknown methods
            raise FiveViewError, "Unknown view method: %s" % name

        # let the ZPublisher do the calling, its security kicks in
        return method_on_view
