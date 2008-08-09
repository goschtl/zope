##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Helpers for the zope.introspectorui.
"""
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.component import getMultiAdapter

def code_breadcrumbs(url, dotted_name):
    """Breadcrumbs for code objects.

    The `url` parameter should be a link to the object denoted by the
    dotted name `dotted_name``.
    """
    url_parts = url.split('/')
    dotted_name_parts = dotted_name.split('.')
    start_len = len(url_parts) - len(dotted_name_parts)
    url_start = '/'.join(url_parts[:start_len])
    result = []
    for name in dotted_name_parts:
        url_start = '/'.join([url_start, name])
        result.append(dict(name=name, url=url_start))
    return tuple(result)
