import grok
from grokstar.blog import Blog,Drafts
from grokstar.calendar import Year

class BlogTraverser(grok.Traverser):
    grok.context(Blog)

    def traverse(self, name):
        #import pdb;pdb.set_trace()
        if name == "drafts":
            drafts =  Drafts()
            drafts.__name__ = 'drafts'
            drafts.__parent__ = self.context
            return drafts
        try:
            year = int(name)
        except ValueError:
            return self.entry_traverse(name)
        return Year(year)

    def entry_traverse(self, name):
        return self.context['entries'].get(name, None)
