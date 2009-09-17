from megrok.layout import Layout, Page
from zope.app.folder.interfaces import IRootFolder


class AdminLayout(Layout):
    """The general layout for the administration
    """
    grok.context(IRootFolder)
    

class AdminView(Page):
    """An admin view.
    """
    grok.baseclass()
    grok.context(IRootFolder)
