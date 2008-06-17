import grok

from grokstar.blog import Blog, lastEntries

class RSS(grok.View):
    grok.context(Blog)
    grok.name('feed.rss')
                
    def items(self, max=10):
        return lastEntries(max)