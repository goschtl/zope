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
"""Helpers for the grokui.introspector.
"""

def dotted_name_url(dotted_path, preserve_last=0):
    """Create an HTML fragment with links to parts of a dotted name.
    """
    result = []
    parts = dotted_path.split('.', len(dotted_path.split('.'))
                              - 1 - preserve_last)
    for i in range(0, len(parts)):
        part = '<a href="/++inspect++/+code/%s">%s</a>' % (
            '/'.join(parts[0:i+1]), parts[i])
        result.append(part)
    return '.'.join(result)

def get_url_with_namespaces(request, url):
    """Insert any missing namespaces in an URL.
    """
    app_url = request.getApplicationURL()
    url_parts = [app_url]
    for name in request._traversed_names:
        if not name.startswith('++') or not name.endswith('++'):
            break
        if name not in url:
            url_parts.append(name)
    url_parts.append(url.split(app_url, 1)[1][1:])
    return '/'.join(url_parts)
