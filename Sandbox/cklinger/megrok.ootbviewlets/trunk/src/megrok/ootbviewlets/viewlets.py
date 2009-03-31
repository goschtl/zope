import grok
from z3c.menu.simple.menu import (ContextMenuItem, GlobalMenuItem,
               TabItem, ActionItem)

class ContextViewlet(ContextMenuItem, grok.Viewlet):
    """ Viewlet based on a specific context 
    """
    grok.baseclass()


class GlobalMenuViewlet(GlobalMenuItem, grok.Viewlet):
    """Viewlet based on a specific site
    """
    grok.baseclass()


class TabItem(TabItem, grok.Viewlet):
    """Viewlet which renders as a Tab Item
    """
    grok.baseclass()

    def render(self):
        return self.template()


class ActionItem(ActionItem, grok.Viewlet):
    """Viewlet which renders as a Action Item
    """
    grok.baseclass()

    def render(self):
        return self.template()

