"""Components for megrok.feeds.
"""
import vice.outbound.core
from vice.outbound.core.browser.feed import Atom_1_0_FeedView


class AtomFeed(Atom_1_0_FeedView):
    pass
    #grok.context(IFeedable)
