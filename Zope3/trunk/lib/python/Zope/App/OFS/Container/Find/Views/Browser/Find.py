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
"""

$Id: Find.py,v 1.3 2002/07/11 18:21:29 jim Exp $
"""

from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.OFS.Container.Find.IFind import IFind
# XXX this needs to be looked up in a registry
from Zope.App.OFS.Container.Find.FindAdapter import SimpleIdFindFilter

from Zope.ComponentArchitecture import getAdapter, getView

from Zope.Publisher.Browser.BrowserView import BrowserView

# XXX very simple implementation right now
class Find(BrowserView):
    
    index = ViewPageTemplateFile('find.pt')
        
    def findByIds(self, ids):
        """Do a find for the ids listed in ids, which is a string.
        """
        finder = getAdapter(self.context, IFind)
        ids = ids.split()
        # if we don't have any ids listed, don't search at all
        if not ids:
            return []
        request = self.request
        result = []
        for object in finder.find([SimpleIdFindFilter(ids)]):
            id = getId(object)
            url = str(getView(object, 'absolute_url', request))
            result.append({ 'id': id, 'url': url})
        return result
    
from Zope.Proxy.ContextWrapper import getInnerWrapperData

# XXX get the id of an object (should be imported from somewhere)
def getId(object):
    dict = getInnerWrapperData(object)
    if dict:
        return dict.get('name')
    return None
