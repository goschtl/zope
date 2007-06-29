##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Resource License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: app.py 44 2007-02-21 09:43:39Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks
from zope.viewlet import viewlet


from z3c.website import interfaces
import z3c.website.layer


class EditTool(viewlet.ViewletBase):
    """Edit tool."""

    viewNames = {'View':'index.html',
                 'Edit':'edit.html',
                 'Meta':'meta.html'}

    def samples(self):
        # prevent edit links on add forms
        res = []
        if interfaces.ISampleAddForm.providedBy(self.__parent__):
            return res
        append = res.append
        try:
            baseURL = absoluteURL(self.context, self.request)
            for title, name in self.viewNames.items():
                info = {}
                info['url'] = baseURL+'/'+name
                info['title'] = title
                append(info)
        except KeyError:
            # site does not exist right now
            pass
        return res
