##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id$
"""
__docformat__ = 'restructuredtext'

import urllib

from zope import component

from zope.dublincore.interfaces import IZopeDublinCore
from zope.security.interfaces import Unauthorized
from zope.size.interfaces import ISized
from zope.app.container.browser.contents import Contents

class NoZODBContents(Contents):

    """handles contents without zodb

    >>> from zope.publisher.browser import TestRequest
    >>> class Content(object):pass
    >>> obj = Content()
    >>> obj.title=u"some title"
    >>> from zope import interface
    >>> interface.directlyProvides(obj, IZopeDublinCore)
    >>> request = TestRequest()
    >>> v = NoZODBContents({}, request)
    >>> v.context['first'] = obj
    >>> v.request = request
    >>> [i for i in v.listContentInfo()]
    [{'title': u'some title', 'url': 'first',
      'object': <lovely.zetup.browser.views.Content object at ...>,
      'cb_id': 'first', 'id': 'first', 'icon': None}]
    """

    def listContentInfo(self):
        for id, obj in self.context.items():
            info = {}
            info['id'] = info['cb_id'] = id
            info['object'] = obj
            info['url'] = urllib.quote(id.encode('utf-8'))
            zmi_icon = component.queryMultiAdapter((obj,
                                                    self.request),
                                                   name='zmi_icon')
            if zmi_icon is None:
                info['icon'] = None
            else:
                info['icon'] = zmi_icon()
            dc = IZopeDublinCore(obj, None)
            if dc is not None:
                title = self.safe_getattr(dc, 'title', None)
                if title:
                    info['title'] = title
                formatter = self.request.locale.dates.getFormatter(
                    'dateTime', 'short')
                created = self.safe_getattr(dc, 'created', None)
                if created is not None:
                    info['created'] = formatter.format(created)
                modified = self.safe_getattr(dc, 'modified', None)
                if modified is not None:
                    info['modified'] = formatter.format(modified)
            sized_adapter = ISized(obj, None)
            if sized_adapter is not None:
                info['size'] = sized_adapter
            yield info

