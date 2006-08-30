from zope import interface
from zope.publisher.interfaces.browser import IBrowserView

class ILiveSearchView(IBrowserView):
    """A view which renders the livesearch input field"""

class ILiveSearchResultsView(IBrowserView):
    """A view which renders the livesearch results"""
    
