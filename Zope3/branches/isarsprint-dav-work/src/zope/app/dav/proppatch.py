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

$Id$
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
        if self.content_type not in ['text/xml', 'application/xml']:
            self.request.response.setStatus(400)
            return ''

        resource_url = str(zapi.getView(self.context, 'absolute_url', 
                                        self.request))
        if IReadContainer.providedBy(self.context):
            resource_url += '/'

        self.request.bodyFile.seek(0)
        xmldoc = minidom.parse(self.request.bodyFile)
        resp = minidom.Document()
        ms = resp.createElement('multistatus')
        ms.setAttribute('xmlns', self.default_ns)
        resp.appendChild(ms)
        ms.appendChild(resp.createElement('response'))
        ms.lastChild.appendChild(resp.createElement('href'))
        ms.lastChild.lastChild.appendChild(resp.createTextNode(resource_url))

        body = resp.toxml().encode('utf-8')
        self.request.response.setBody(body)
        self.request.response.setStatus(207)
        return body
