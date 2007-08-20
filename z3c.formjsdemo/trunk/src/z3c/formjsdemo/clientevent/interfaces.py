import zope.interface
from zope.schema import TextLine, Text

class IArticle(zope.interface.Interface):
    """A simple article"""

    title = TextLine(
        title=u'Title',
        required=True)

    subtitle = TextLine(
        title=u'Subtitle',
        required=True)

    body = Text(
        title=u'Body',
        required=False)
