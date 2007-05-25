##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.traversing.browser import absoluteURL
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds

from z3c.pagelet import browser
from z3c.template.interfaces import ILayoutTemplate



class SearchResultPagelet(browser.BrowserPagelet):
    """Search result page"""

    idxName = u'text'
    catalogName = u'WebSiteCatalog'

    def catalogResults(self):
        query = self.request.get('webSiteLiveSearchInput', None)
        if query is None:
            return {}
        query = u'%s*' % query
        catalog = zope.component.getUtility(ICatalog, name=self.catalogName)
        results = catalog.apply({self.idxName:query})
        return results

    def results(self):
        uidutil = zope.component.getUtility(IIntIds)
        for uid, score in self.catalogResults().items():
            obj = uidutil.getObject(uid)
            info = {}
            info['obj'] = obj
            info['title'] = obj.title
            info['description'] = obj.description
            info['url'] = absoluteURL(obj, self.request)
            info['score'] = "%.4f" % score
            yield info

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)