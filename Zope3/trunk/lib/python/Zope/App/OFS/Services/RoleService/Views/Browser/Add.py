from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.RoleService.Role import Role
from Zope.App.OFS.Services.RoleService.RoleService import ILocalRoleService


class Add(BrowserView):
    "Provide a user interface for adding a contact"
    
    __used_for__ = ILocalRoleService

    def action(self, id, title, description):
        "Add a contact"
        role = Role(id, title, description)
        self.context.setObject(id, role)
        self.request.response.redirect('.')

