from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from lovely.rating.interfaces import IRatable, IRatingsManager
from pytz import UTC

def evolve(context):
    """Add tzinfo to timestamp of ratings"""
    for ratable in findObjectsProviding(getRootFolder(context), IRatable):
        manager = IRatingsManager(ratable)
        for d in manager._storage.values():
            for rating in d.values():
                if rating._timestamp.tzinfo is None:
                    rating._timestamp = rating._timestamp.replace(
                        tzinfo=UTC)
                    
