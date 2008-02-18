import grok
from hurry.query.query import Query
from hurry import query
from zope.interface import Interface
from grokstar.interfaces import IBlog

class ViewBase(grok.View):
    """contain common view methods"""
    grok.context(Interface)

    def numPosts(self):
        # @@ is there a better way to get all entries through the catalog?
        obj = self.context
        while obj is not None:
            if IBlog.providedBy(obj):
                return len(obj['entries'])
            obj = obj.__parent__
        return 0
