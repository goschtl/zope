##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""WebDAV method PROPPATCH

$Id: propfind.py 27237 2004-08-23 23:42:11Z jim $
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom

from zope.app import zapi
from zope.app.container.interfaces import IReadContainer

class PROPPATCH(object):
    """PROPPATCH handler for all objects"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        ct = request.getHeader('content-type', 'text/xml')
        if ';' in ct:
            parts = ct.split(';', 1)
            self.content_type = parts[0].strip().lower()
            self.content_type_params = parts[1].strip()
        else:
            self.content_type = ct.lower()
            self.content_type_params = None
        self.default_ns = 'DAV:'

    def PROPPATCH(self):
        request = self.request
        resource_url = str(zapi.getView(self.context, 'absolute_url', request))
        if IReadContainer.providedBy(self.context):
            resource_url = resource_url + '/'
        data = request.bodyFile
        data.seek(0)
        response = ''
        body = ''

        if self.content_type not in ['text/xml', 'application/xml']:
            request.response.setStatus(400)
            return body

        xmldoc = minidom.parse(data)
        response = minidom.Document()
        ms = response.createElement('multistatus')
        ms.setAttribute('xmlns', self.default_ns)
        response.appendChild(ms)
        re = response.createElement('response')
        ms.appendChild(re)
        href = response.createElement('href')
        re.appendChild(href)
        r_url = response.createTextNode(resource_url)
        href.appendChild(r_url)

        body = response.toxml().encode('utf-8')
        request.response.setBody(body)
        request.response.setStatus(207)
        return body
