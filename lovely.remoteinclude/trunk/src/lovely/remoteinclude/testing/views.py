from lovely.remoteinclude.view import IncludeableView
from zope import interface
from lovely.responsecache.view import ResponseCacheSettings

class Inc3View(IncludeableView):

    def render(self):
        return "inc3 should not be seen in test"

class HourCacheSettings(ResponseCacheSettings):
    lifetime=3600
    
