import grok
from z3c.menu.simple.menu import (ContextMenuItem, GlobalMenuItem,
               TabItem)

class ContextViewlet(ContextMenuItem, grok.Viewlet):
    grok.baseclass()


class GlobalMenuViewlet(GlobalMenuItem, grok.Viewlet):
    grok.baseclass()

class TabItem(TabItem, grok.Viewlet):
    grok.baseclass()

    def render(self):
        return self.template()

