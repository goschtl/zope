from Products.Five.browser import BrowserView

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize

class FeatureView(BrowserView):
    """ Default view for chain. This class contains all python that we need for
        Feature objects.
    """
    def tag(self, **kwargs):
        return self.context.getField('image').tag(self.context, **kwargs)
    
    def blurb(self):
        return self.context.getBlurb()
        
    def divider(self):
        return self.context.getDivider()