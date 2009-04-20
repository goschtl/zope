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
from zope.component import createObject, getMultiAdapter
from zope.publisher.browser import TestRequest
from zope.introspectorui.util import (_format_dict, dedent_string,
                                      get_doc_format,)

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

def render_text(text, module=None, format=None, dedent=True):
    if not text:
        return u''

    if module is not None:
        if isinstance(module, (str, unicode)):
            module = sys.modules.get(module, None)
        format = get_doc_format(module)

    if format is None:
        format = 'zope.source.rest'

    assert format in _format_dict.values()

    text = dedent_string(text)

    if not isinstance(text, unicode):
        text = text.decode('latin-1', 'replace')
    source = createObject(format, text)

    renderer = getMultiAdapter((source, TestRequest()))
    return renderer.render()

def render_docstring(docstring, heading_only=False, format=None):
    """Get the doc string of the module ReST formatted.
    """
    if docstring is None:
        return u''
    lines = docstring.strip().split('\n')
    if len(lines) and heading_only:
        # Find first empty line to separate heading from trailing text.
        headlines = []
        for line in lines:
            if line.strip() == "":
                break
            headlines.append(line)
        lines = headlines
    # Get rid of possible CVS id.
    lines = [line for line in lines if not line.startswith('$Id')]
    return render_text('\n'.join(lines), format=format)
