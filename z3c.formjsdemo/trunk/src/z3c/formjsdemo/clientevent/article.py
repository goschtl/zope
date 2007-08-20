import persistent
import zope.interface
from zope.schema.fieldproperty import FieldProperty

import interfaces

class Article(persistent.Persistent):

    zope.interface.implements(interfaces.IArticle)

    title = FieldProperty(interfaces.IArticle['title'])
    subtitle = FieldProperty(interfaces.IArticle['subtitle'])
    body = FieldProperty(interfaces.IArticle['body'])
