# For Views

from zope.app.browser.services.service import Adding
from zope.context import ContextSuper
from zope.app.interfaces.services.pluggableauth import IPrincipalSource
        
class PrincipalSourceAdding(Adding):
    """Adding subclass used for principal sources."""

    menu_id = "add_principal_source"

    def add(self, content):

        if not IPrincipalSource.isImplementedBy(content):
            raise TypeError("%s is not a readable principal source" % content)

        return ContextSuper(PrincipalSourceAdding, self).add(content)
