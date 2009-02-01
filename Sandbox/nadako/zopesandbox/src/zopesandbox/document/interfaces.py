from zope.interface import Interface
from zope.schema import Text, TextLine

class IDocument(Interface):

    title = TextLine(title=u'Title', required=True)
    description = Text(title=u'Description', required=False)
    body = Text(title=u'Body text', required=False)
