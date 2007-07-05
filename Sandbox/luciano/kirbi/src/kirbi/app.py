import grok
from kirbi.pac import Pac
from kirbi.book import Book
from grok import index

class Kirbi(grok.Application, grok.Container):
    """ Peer-to-peer library system """
    def __init__(self):
        super(Kirbi, self).__init__()
        self['pac'] = Pac()

class Index(grok.View):
    pass # see app_templates/index.pt

class BookIndexes(grok.Indexes):
    grok.site(Kirbi)
    grok.context(Book)

    title = index.Text()
    isbn13 = index.Field()