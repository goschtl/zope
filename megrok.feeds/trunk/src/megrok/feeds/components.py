"""Components for megrok.feeds.
"""
from vice.outbound.core.browser.feed import Atom_1_0_FeedView
from zope.interface import Interface

class IFeedable(Interface):
    pass # marker interface

class AtomFeed(Atom_1_0_FeedView):
    pass
