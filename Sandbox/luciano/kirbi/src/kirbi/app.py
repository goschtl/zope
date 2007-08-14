import grok
from grok import index
from kirbi.pac import Pac
from kirbi.book import Book
from kirbi.user import UserFolder
from zope.interface import Interface, implements
from zope.component import getSiteManager

class Kirbi(grok.Application, grok.Container):
    """Peer-to-peer library system."""
    def __init__(self):
        super(Kirbi, self).__init__()
        self['pac'] = Pac()
        self.userFolder = self['u'] = UserFolder()

class Index(grok.View):
    pass

class BookIndexes(grok.Indexes):
    grok.site(Kirbi)
    grok.context(Book)

    title = index.Text()
    isbn13 = index.Field()
    searchableText = index.Text()
    
    #XXX: check whether this is working:
    # the creatorSet book method was not being called
    creatorsSet = index.Set()
    
class Master(grok.View):
    """The master page template macro."""
    grok.context(Interface)
