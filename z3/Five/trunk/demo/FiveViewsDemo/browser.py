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

class SimpleFolderView(BrowserView):
    security = ClassSecurityInfo()

    security.declarePublic('eagle')
    def eagle(self):
        """Test
        """
        return "The eagle has landed: %s" % self.context.objectIds()

    security.declareProtected('View management screens', 'mydefault')
    def mydefault(self):
        """Test
        """
        return "This is default view for %s" % self.context.absolute_url()
    
InitializeClass(SimpleFolderView)
