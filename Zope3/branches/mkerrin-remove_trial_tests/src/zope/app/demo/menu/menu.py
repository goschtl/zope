##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Special Menu Implementations

$Id$
"""
__docformat__ = "reStructuredText"
from zope.interface import implements

from zope.app import zapi
from zope.app.component.hooks import getSite
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.publisher.interfaces.browser import IBrowserMenu


class RecentlyOpened(object):
    """Menu showing recently opened files.

    This implementation is actually a quick hack and will display all of the
    items in a container.
    """
    implements(IBrowserMenu)
    
    def __init__(self, id, title=u'', description=u''):
        self.id = id
        self.title = title
        self.description = description

    def getMenuItems(self, object, request):
        """Return menu item entries in a TAL-friendly form."""
        result = []
        site = getSite()
        url = zapi.absoluteURL(site, request)        

        for name, item in object.items():
            dc = IZopeDublinCore(item, None)
            zmi_icon = zapi.queryMultiAdapter((item, request), name='zmi_icon')

            result.append(
                {'title': name,
                 'description': dc.title,
                 'action': name + '/manage',
                 'selected': u'',
                 'icon': zmi_icon and zmi_icon.url() or None,
                 'extra': {},
                 'submenu': None})
    
        return result
