##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Find View Class

$Id: find.py,v 1.4 2003/08/06 14:41:36 srichter Exp $
"""
# XXX this needs to be looked up in a registry
from zope.app.container.find import SimpleIdFindFilter
from zope.app.interfaces.container.find import IFind
from zope.app.traversing import getName
from zope.component import getAdapter, getView
from zope.context import getInnerWrapperData
from zope.publisher.browser import BrowserView


# XXX very simple implementation right now
class Find(BrowserView):

    def findByIds(self, ids):
        """Do a find for the ids listed in ids, which is a string."""
        finder = getAdapter(self.context, IFind)
        ids = ids.split()
        # if we don't have any ids listed, don't search at all
        if not ids:
            return []
        request = self.request
        result = []
        for object in finder.find([SimpleIdFindFilter(ids)]):
            url = str(getView(object, 'absolute_url', request))
            result.append({ 'id': getName(object), 'url': url})
        return result
