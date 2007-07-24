import zope.component
import zope.interface
from zope.schema.fieldproperty import FieldProperty

import grok

import mars.layer

from tfws.website import interfaces
from tfws.website.layer import IWebSiteLayer

mars.layer.layer(IWebSiteLayer)

class Page(grok.Container):
    """Mars/Grok/Z3C page.

    """
    zope.interface.implements(interfaces.IPage)

    title = FieldProperty(interfaces.IPage['title'])
    description = FieldProperty(interfaces.IPage['description'])
    keyword = FieldProperty(interfaces.IPage['keyword'])
    body = FieldProperty(interfaces.IPage['body'])

    def __init__(self, title=u'', description=u'',
                       keyword=u'', body=u''):
        super(Page, self).__init__()
        self.title = title
        self.description = description
        self.keyword = keyword
        self.body = body

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)

