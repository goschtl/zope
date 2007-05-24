###############################################################################
#
# Copyright 2006 by refline (Schweiz) AG, CH-5630 Muri
#
###############################################################################
"""``refline`` TALES Namespace implementation

$Id: api.py 1426 2006-11-10 04:05:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema
from zope.security.interfaces import Unauthorized
from zope.app import zapi


class ITitle(zope.interface.Interface):
    """Provide a title for the page"""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the IContent object.',
        required=True)


class Title(object):
    """Generic Title implementation"""
    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(ITitle)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        try:
            title = getattr(self.context, 'title', None)
        except Unauthorized:
            title = None

        if title is None:
            title = zapi.name(self.context)

        return title or u''


class IWebSiteTalesAPI(zope.interface.Interface):
    """Provide a title for the page"""

    page_title = zope.schema.TextLine(
        title=u'Page title',
        description=u'The title of the page.',
        required=True)


class WebSiteTalesAPI(object):

    zope.interface.implements(IWebSiteTalesAPI)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        self._engine = engine

    @property
    def title(self):
        return ITitle(self.context).title
