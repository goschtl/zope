from Products.Five.api import BrowserView

class SimpleContentView(BrowserView):
    """More docstring. Please Zope"""

    def eagle(self):
        """Docstring"""
        return "The eagle has landed"

class SimpleFolderView(BrowserView):

    def eagle(self):
        """Test
        """
        return "The eagle has landed: %s" % self.context.objectIds()

    def mydefault(self):
        """Test
        """
        return "This is default view for %s" % self.context.absolute_url()
