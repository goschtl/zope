from zope.publisher.browser import BrowserView
from zope.app.services.role import Role
from zope.app.services.role import ILocalRoleService


class Add(BrowserView):
    "Provide a user interface for adding a contact"

    __used_for__ = ILocalRoleService

    def action(self, id, title, description):
        "Add a contact"
        role = Role(id, title, description)
        self.context.setObject(id, role)
        self.request.response.redirect('.')



""" Define view component for service manager contents.

$Id: role.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""

from zope.app.browser.container.contents import Contents

class Contents(Contents):
    pass
