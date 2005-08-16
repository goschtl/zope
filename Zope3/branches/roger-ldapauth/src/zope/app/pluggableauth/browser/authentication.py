#
from zope.interface import implements
from zope.component.interfaces import IViewFactory
from zope.app.security.interfaces import ILoginPassword



class PrincipalAuthenticationView:
    """Simple basic authentication view

    This only handles requests which have basic auth credentials
    in them currently (ILoginPassword-based requests).
    If you want a different policy, you'll need to write and register
    a different view, replacing this one.
    
    """
    implements(IViewFactory)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def authenticate(self):
        a = ILoginPassword(self.request, None)
        if a is None:
            return
        login = a.getLogin()
        password = a.getPassword()

        p = self.context.authenticate(login, password)
        return p
