from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.Five.api import BrowserView

class SimpleContentView(BrowserView):
    """More docstring. Please Zope"""
    security = ClassSecurityInfo()

    security.declareProtected('View Management Screens', 'eagle')
    def eagle(self):
        """Docstring"""
        return "The eagle has landed"

InitializeClass(SimpleContentView)
