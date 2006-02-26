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
"""WebDAV method PROPFIND

$Id$
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom
from xml.parsers import expat

from zope import component
from zope.app.container.interfaces import IReadContainer

from interfaces import INamespaceRegistry
from common import MultiStatus

class PROPFIND(object):
    """PROPFIND handler for all objects"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.setDepth(request.getHeader('depth', 'infinity'))
        ct = request.getHeader('content-type', 'text/xml')
        if ';' in ct:
            parts = ct.split(';', 1)
            self.content_type = parts[0].strip().lower()
            self.content_type_params = parts[1].strip()
        else:
            self.content_type = ct.lower()
            self.content_type_params = None
        self.default_ns = 'DAV:'

        self.responsedoc = MultiStatus()

    def getDepth(self):
        return self._depth

    def setDepth(self, depth):
        self._depth = depth.lower()

    def PROPFIND(self):
        if self.content_type not in ('text/xml', 'application/xml'):
            self.request.response.setStatus(400)
            return ''
        if self.getDepth() not in ['0', '1', 'infinity']:
            self.request.response.setStatus(400)
            return ''

        try:
            xmldoc = minidom.parse(self.request.bodyStream)
        except expat.ExpatError:
            xmldoc = None # request body is empty ???

        self.handlePropfind(xmldoc)

        body = self.responsedoc.body.toxml('utf-8')
        self.request.response.setResult(body)
        self.request.response.setStatus(207)
        self.request.response.setHeader('content-type', 'text/xml')

        return body

    def handlePropfind(self, xmldoc):
        resp = self.resp = \
               self.responsedoc.addResponse(self.context, self.request)

        nr = component.getUtility(INamespaceRegistry, context = self.context)

        if xmldoc is not None:
            propname = xmldoc.getElementsByTagNameNS(
                self.default_ns, 'propname')
            if propname:
                self._renderPropnameResponse(nr, resp)
            else:
                source = xmldoc.getElementsByTagNameNS(self.default_ns, 'prop')
                if len(source) == 0:
                    self._renderAllProperties(nr, resp)
                elif len(source) == 1:
                    self._renderSelectedProperties(nr, resp, source[0])
                else:
                    raise Exception, "something has gone wrong here"
        else:
            self._renderAllProperties(nr, resp)

        self._depthRecurse(xmldoc)

    def _depthRecurse(self, xmldoc):
        depth = self.getDepth()
        if depth == '0' or not IReadContainer.providedBy(self.context):
            return

        subdepth = (depth == '1') and '0' or 'infinity'

        for id, obj in self.context.items():
            pfind = PROPFIND(obj, self.request)
            pfind.setDepth(subdepth)
            pfind.handlePropfind(xmldoc)

            subrespdoc = pfind.responsedoc.body
            responses = subrespdoc.getElementsByTagNameNS(self.default_ns,
                                                          'response')
            for r in responses:
                self.responsedoc.appendResponse(r)

    def _renderAllProperties(self, nsregistry, response):
        count = 0

        for nsmanager in nsregistry.getAllNamespaceManagers():
            namespace = nsmanager.namespace
            ns_prefix = None
            if namespace != self.default_ns:
                ns_prefix = 'a%s' % count
                count += 1

            for propname in nsmanager.getAllPropertyNames(self.context):
                widget = nsmanager.getWidget(self.context, self.request,
                                             propname, ns_prefix)
                el = widget.renderProperty()
                response.addPropertyByStatus(namespace, ns_prefix, el, 200)

    def _renderSelectedProperties(self, nsregistry, response, source):
        count = 0
        renderedns = {}

        for node in source.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            namespace = node.namespaceURI
            propname = node.localName
            status = 200

            ns_prefix = None
            if not renderedns.has_key(namespace) and \
                   namespace != self.default_ns:
                ns_prefix = 'a%s' % count
                count += 1
            elif namespace != self.default_ns:
                ns_prefix = renderedns[namespace]

            nsmanager = nsregistry.queryNamespaceManager(namespace,
                                                         default = None)

            if nsmanager is not None and \
                   nsmanager.queryProperty(self.context,
                                           propname, None) is not None:
                widget = nsmanager.getWidget(self.context, self.request,
                                             propname, ns_prefix)
                el = widget.renderProperty()
            else:
                status = 404
                el = response.createEmptyElement(namespace, ns_prefix,
                                                 propname)

            response.addPropertyByStatus(namespace, ns_prefix, el, status)

    def _renderPropnameResponse(self, nsregistry, response):
        count = 0
        for nsmanager in nsregistry.getAllNamespaceManagers():
            namespace = nsmanager.namespace
            if namespace != self.default_ns:
                ns_prefix = 'a%s' % count
                count += 1
            else:
                ns_prefix = None

            for propname in nsmanager.getAllPropertyNames(self.context):
                el = response.createEmptyElement(namespace, ns_prefix, propname)
                response.addPropertyByStatus(namespace, ns_prefix, el, 200)
