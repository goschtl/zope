import grok
from grok import index
from kirbi.pac import Pac
from kirbi.book import Book
from kirbi.user import UserFolder
from zope.interface import Interface, implements
from zope.component import getSiteManager
from zope.traversing import browser

PAC_NAME = u'pac'
USER_FOLDER_NAME = u'u'

grok.define_permission('kirbi.Join')
grok.define_permission('kirbi.EditBook')
grok.define_permission('kirbi.DeleteBook')

class Kirbi(grok.Application, grok.Container):
    """Peer-to-peer library system."""
    def __init__(self):
        global sitePac, siteUsers, siteUsersURL
        super(Kirbi, self).__init__()
        self.pac = self[PAC_NAME] = Pac()
        self.user_folder = self[USER_FOLDER_NAME] = UserFolder()

class Index(grok.View):

    def pac_url(self):
        return self.url(self.context.pac)

    def login_url(self):
        return self.url(self.context.user_folder,'login')

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
    # register this view for all objects
    grok.context(Interface)
