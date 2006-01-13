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

from zope.schema import getFieldNamesInOrder, getFields
from zope.publisher.http import status_reasons

from zope.app import zapi
from zope.app.container.interfaces import IReadContainer
from zope.app.form.utility import setUpWidget

from interfaces import IDAVWidget, IDAVNamespace
from opaquenamespaces import IDAVOpaqueNamespaces
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

        self.oprops = IDAVOpaqueNamespaces(self.context, None)
        _avail_props = {}
        # List all *registered* DAV interface namespaces and their properties
        for ns, iface in zapi.getUtilitiesFor(IDAVNamespace):
            _avail_props[ns] = getFieldNamesInOrder(iface)

        # List all opaque DAV namespaces and the properties we know of
        if self.oprops:
            for ns, oprops in self.oprops.items():
                _avail_props[ns] = list(oprops.keys())
        self.avail_props = _avail_props

        self.responsedoc = MultiStatus()

    def getDepth(self):
        return self._depth

    def setDepth(self, depth):
        self._depth = depth.lower()

    def PROPFIND(self, xmldoc = None):
        if self.content_type not in ('text/xml', 'application/xml'):
            self.request.response.setStatus(400)
            return ''
        if self.getDepth() not in ['0', '1', 'infinity']:
            self.request.response.setStatus(400)
            return ''

        if xmldoc is None:
            try:
                xmldoc = minidom.parse(self.request.bodyStream)
            except expat.ExpatError:
                pass

        self.handlePropfind(xmldoc)

        body = self.responsedoc.body.toxml('utf-8')
        self.request.response.setResult(body)
        self.request.response.setStatus(207)
        self.request.response.setHeader('content-type', 'text/xml')

        return body

    def handlePropfind(self, xmldoc):
        resp = self.resp = \
               self.responsedoc.addResponse(self.context, self.request)

        if xmldoc is not None:
            propname = xmldoc.getElementsByTagNameNS(
                self.default_ns, 'propname')
            if propname:
                self._handlePropname(resp)
            else:
                source = xmldoc.getElementsByTagNameNS(self.default_ns, 'prop')
                self._handlePropvalues(source)
        else:
            self._handlePropvalues(None)

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
                ## print "obj: %s, %s" %(zapi.getPath(obj), r.toxml('utf-8'))
                self.responsedoc.appendResponse(r)

    def _handleProp(self, source):
        props = {}
        source = source[0]

        for node in source.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue

            ns = node.namespaceURI
            iface = zapi.queryUtility(IDAVNamespace, ns)
            value = props.get(ns, {'iface': iface, 'props': []})
            value['props'].append(node.localName)
            props[ns] = value

        return props

    def _handleAllprop(self):
        props = {}

        for ns, properties in self.avail_props.items():
            iface = zapi.queryUtility(IDAVNamespace, ns)
            props[ns] = {'iface': iface, 'props': properties}

        return props

    def _handlePropname(self, resp):
        count = 0
        for ns, props in self.avail_props.items():
            attr_name = 'a%s' % count
            ns_prefix = None
            if ns is not None and ns != self.default_ns:
                count += 1
                ns_prefix = attr_name
            for p in props:
                el = resp.createEmptyElement(ns, ns_prefix, p)
                resp.addPropertyByStatus(ns, ns_prefix, el)

    def _handlePropvalues(self, source):
        if not source:
            _props = self._handleAllprop()
        else:
            _props = self._handleProp(source)

        self._renderResponse(self.resp, _props)

    def _renderResponse(self, re, _props):
        count = 0
        # ns - the full namespace for this object.
        for ns, ifaceprops in _props.items():
            attr_name = 'a%s' % count
            ns_prefix = None
            if ns is not None and ns != self.default_ns:
                count += 1
                ns_prefix = attr_name

            iface = ifaceprops['iface']
            props = ifaceprops['props']

            # adapted - the current view through which all properties are
            # reterived this should be moved to using the widget framework.
            if not iface:
                for name in props:
                    if self.oprops:
                        status = 200
                        el = self.oprops.renderProperty(ns, ns_prefix, name)
                        if el is None:
                            # We can't add a None property in the MultiStatus
                            # utility so add an empty property registered has
                            # a 404 stats not found property.
                            status = 404
                            el = re.createEmptyElement(ns, ns_prefix, name)
                        re.addPropertyByStatus(ns, ns_prefix, el, status)
                    else:
                        el = re.createEmptyElement(ns, ns_prefix, name)
                        re.addPropertyByStatus(ns, ns_prefix, el, 404)
                continue

            adapted = iface(self.context, None)
            if adapted is None:
                # XXX - maybe these properties are unavailable for a reason.
                # render unavailable properties
                for propname in props:
                    el = re.createEmptyElement(ns, ns_prefix, propname)
                    re.addPropertyByStatus(ns, ns_prefix, el, 404)
                    continue

            for propname in props:
                status = 200
                el = None # property DOM fragment
                field = None

                try:
                    field = iface[propname]
                except KeyError:
                    # A widget wasn't generated for this property
                    # because the attribute was missing on the adapted
                    # object, which actually means that the adapter
                    # didn't fully implement the interface ;(
                    el = re.createEmptyElement(ns, ns_prefix, propname)
                    status = 404

                    re.addPropertyByStatus(ns, ns_prefix, el, status)
                    continue

                try:
                    setUpWidget(self, propname, field, IDAVWidget,
                                value = field.get(adapted),
                                ignoreStickyValues = False)
                    widget = getattr(self, propname + '_widget', None)
                    assert widget is not None
                    el = widget.renderProperty(ns, ns_prefix)
                    if widget.getErrors():
                        status = 500
                except:
                    # Internal Server Error - status 500
                    el = re.createEmptyElement(ns, ns_prefix, propname)
                    status = 500

                re.addPropertyByStatus(ns, ns_prefix, el, status)
