import grok
from z3c.menu.simple import menu

class TabMenuManager(menu.Tab, grok.ViewletManager):
    grok.baseclass()
    template = grok.PageTemplateFile('templates/tab.pt')

    def render(self):
        """Return the template with the option 'menus'"""
        if not self.viewlets:
            return u''
        return self.template.render(self)

