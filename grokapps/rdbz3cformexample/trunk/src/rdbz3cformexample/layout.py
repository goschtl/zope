import grok
from megrok.layout import Layout
from zope.interface import Interface


class RDBLayout(Layout):
    """The general layout for the RDB application
    """
    grok.context(Interface)
    template = grok.PageTemplateFile('templates/layout.pt')


