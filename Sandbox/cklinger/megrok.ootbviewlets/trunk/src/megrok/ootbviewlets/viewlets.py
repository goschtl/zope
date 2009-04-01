import grok
from zope.app.zapi import absoluteURL
from z3c.menu.simple.menu import (ContextMenuItem, GlobalMenuItem,
               TabItem, ActionItem)

class ContextMenuItem(ContextMenuItem, grok.Viewlet):
    """ Viewlet based on a specific context 
    """
    grok.baseclass()


class GlobalMenuItem(GlobalMenuItem, grok.Viewlet):
    """Viewlet based on a specific site
    """
    grok.baseclass()


class TabItem(TabItem, grok.Viewlet):
    """Viewlet which renders as a Tab Item
    """
    grok.baseclass()

    @property
    def url(self):
        contextURL = absoluteURL(self.context, self.request)
        return contextURL + '/' + self.viewURL

    def render(self):
        return self.template()


class ActionItem(ActionItem, grok.Viewlet):
    """Viewlet which renders as a Action Item
    """
    grok.baseclass()

    @property
    def url(self):
        contextURL = absoluteURL(self.context, self.request)
        return contextURL + '/' + self.viewURL

    def render(self):
        return self.template()

