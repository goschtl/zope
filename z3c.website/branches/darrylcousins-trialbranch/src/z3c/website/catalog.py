###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: catalog.py 367 2007-03-25 15:25:33Z roger.ineichen $
"""

import zope.interface
import zope.component
from zope.index.text import textindex
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.catalog.text import ITextIndex
from zope.app.catalog import catalog
from zope.app.component import hooks
from zope.app.container import contained
from zope.app import intid

from zc.catalog import catalogindex
from z3c.configurator import configurator

from z3c.website import interfaces


class TextIndex(textindex.TextIndex, contained.Contained):

    # not really true but needed by query.Text
    zope.interface.implements(ITextIndex)

    def index_doc(self, docid, obj):
        text = ''
        if interfaces.IContent.providedBy(obj):
            text += obj.title + ' '
            text += obj.description + ' '
            text += obj.keyword + ' '
            text += obj.body
        if interfaces.ISample.providedBy(obj):
            text += ' '
            text += obj.headline + ' '
            text += obj.summary + ' '
            text += obj.author
        return super(TextIndex, self).index_doc(docid, text)

    def __repr__(self):
        return '<%s for IFeed>' %self.__class__.__name__


class AddWebSiteCatalog(configurator.ConfigurationPluginBase):
    """Add a catalog for the site."""

    zope.component.adapts(interfaces.IWebSite)

    def __call__(self, data):
        # Get the local site manager
        sm = self.context.getSiteManager()

        # Create an intid utility
        ids = zope.component.queryUtility(intid.interfaces.IIntIds)
        if ids is None:
            ids = intid.IntIds()
            sm['default']['ids' ] = ids
            sm.registerUtility(ids, intid.interfaces.IIntIds)

        # Create a IFeed catalog
        ctlg = catalog.Catalog()
        sm['default']['WebSiteCatalog'] = ctlg
        sm.registerUtility(ctlg, zope.app.catalog.interfaces.ICatalog,
            name='WebSiteCatalog')

        # Set the site, so that the indices don't go crazy
        originalSite = hooks.getSite()
        hooks.setSite(self.context)

        # Feed text index
        ctlg['text'] = TextIndex()

        # Dublin Core Indices
        ctlg['creator'] = catalogindex.SetIndex('creators', IZopeDublinCore)
        ctlg['created'] = catalogindex.DateTimeValueIndex(
            'created', IZopeDublinCore)

        # Reset the site
        hooks.setSite(originalSite)
