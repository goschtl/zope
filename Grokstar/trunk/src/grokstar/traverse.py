import grok
from grokstar.blog import Blog
from grokstar.calendar import Year

class BlogTraverser(grok.Traverser):
    grok.context(Blog)

    def traverse(self, name):
        try:
            year = int(name)
        except ValueError:
            return self.entry_traverse(name)
        return Year(year)

    def entry_traverse(self, name):
        return self.context['entries'].get(name, None)
