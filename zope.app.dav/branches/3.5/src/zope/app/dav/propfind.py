##############################################################################
# Copyright (c) 2003 Zope Foundation and Contributors.
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
from zope.component import getUtilitiesFor, queryMultiAdapter, queryUtility
from zope.schema import getFieldNamesInOrder, getFields
from zope.container.interfaces import IReadContainer
from zope.app.form.utility import setUpWidgets
from zope.security import proxy
from zope.traversing.browser.absoluteurl import absoluteURL

from interfaces import IDAVWidget, IDAVNamespace
from opaquenamespaces import IDAVOpaqueNamespaces

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
        for ns, iface in getUtilitiesFor(IDAVNamespace):
            _avail_props[ns] = getFieldNamesInOrder(iface)
        # List all opaque DAV namespaces and the properties we know of
        if self.oprops:
            for ns, oprops in self.oprops.items():
                _avail_props[ns] = list(oprops.keys())
        self.avail_props = _avail_props

        # The xmldoc attribute will be set later, if needed.
        self.xmldoc = None

    def getDepth(self):
        return self._depth

    def setDepth(self, depth):
        self._depth = depth.lower()

    def PROPFIND(self, xmldoc=None):
        if self.content_type not in ['text/xml', 'application/xml']:
            self.request.response.setStatus(400)
            return ''
        if self.getDepth() not in ['0', '1', 'infinity']:
            self.request.response.setStatus(400)
            return ''

        resource_url = absoluteURL(self.context, self.request)
        if IReadContainer.providedBy(self.context):
            resource_url += '/'

        if xmldoc is None:
            try:
                xmldoc = minidom.parse(self.request.bodyStream)
            except expat.ExpatError:
                pass

        self.xmldoc = xmldoc

        resp = minidom.Document()
        ms = resp.createElement('multistatus')
        ms.setAttribute('xmlns', self.default_ns)
        resp.appendChild(ms)
        ms.appendChild(resp.createElement('response'))
        ms.lastChild.appendChild(resp.createElement('href'))
        ms.lastChild.lastChild.appendChild(resp.createTextNode(resource_url))

        if xmldoc is not None:
            propname = xmldoc.getElementsByTagNameNS(
                self.default_ns, 'propname')
            if propname:
                self._handlePropname(resp)
            else:
                source = xmldoc.getElementsByTagNameNS(self.default_ns, 'prop')
                self._handlePropvalues(source, resp)
        else:
            self._handlePropvalues(None, resp)

        self._depthRecurse(ms)

        body = resp.toxml('utf-8')
        self.request.response.setResult(body)
        self.request.response.setStatus(207)
        self.request.response.setHeader('content-type', 'text/xml')
        return body

    def _depthRecurse(self, ms):
        depth = self.getDepth()
        if depth == '0' or not IReadContainer.providedBy(self.context):
            return
        subdepth = (depth == '1') and '0' or 'infinity'
        for id, obj in self.context.items():
            pfind = queryMultiAdapter((obj, self.request), name='PROPFIND')
            if pfind is None:
                continue
            pfind.setDepth(subdepth)
            value = pfind.PROPFIND(self.xmldoc)
            parsed = minidom.parseString(value)
            responses = parsed.getElementsByTagNameNS(
                self.default_ns, 'response')
            for r in responses:
                ms.appendChild(ms.ownerDocument.importNode(r, True))

    def _handleProp(self, source):
        props = {}
        source = source[0]
        childs = [e for e in source.childNodes
                  if e.nodeType == e.ELEMENT_NODE]
        for node in childs:
            ns = node.namespaceURI
            iface = queryUtility(IDAVNamespace, ns)
            value = props.get(ns, {'iface': iface, 'props': []})
            value['props'].append(node.localName)
            props[ns] = value
        return props

    def _handleAllprop(self):
        props = {}
        for ns, properties in self.avail_props.items():
            iface = queryUtility(IDAVNamespace, ns)
            props[ns] = {'iface': iface, 'props': properties}
        return props

    def _handlePropname(self, resp):
        re = resp.lastChild.lastChild
        re.appendChild(resp.createElement('propstat'))
        prop = resp.createElement('prop')
        re.lastChild.appendChild(prop)
        count = 0
        for ns, props in self.avail_props.items():
            attr_name = 'a%s' % count
            if ns is not None and ns != self.default_ns:
                count += 1
                prop.setAttribute('xmlns:%s' % attr_name, ns)
            for p in props:
                el = resp.createElement(p)
                prop.appendChild(el)
                if ns is not None and ns != self.default_ns:
                    el.setAttribute('xmlns', attr_name)
        re.lastChild.appendChild(resp.createElement('status'))
        re.lastChild.lastChild.appendChild(
            resp.createTextNode('HTTP/1.1 200 OK'))

    def _handlePropvalues(self, source, resp):
        if not source:
            _props = self._handleAllprop()
        else:
            _props = self._handleProp(source)

        avail, not_avail = self._propertyResolver(_props)
        if avail:
            self._renderAvail(avail, resp, _props)
        if not_avail:
            self._renderNotAvail(not_avail, resp)

    def _propertyResolver(self, _props):
        avail = {}
        not_avail = {}
        for ns in _props.keys():
            iface = _props[ns]['iface']
            for p in _props[ns]['props']:
                if iface is None:
                    # The opaque property case
                    if (self.oprops is not None and
                        self.oprops.get(ns, {}).has_key(p)):
                        l = avail.setdefault(ns, [])
                        l.append(p)
                    else:
                        l = not_avail.setdefault(ns, [])
                        l.append(p)
                    continue
                # The registered namespace case
                adapter = iface(self.context, None)
                if adapter is None:
                    # Registered interface but no adapter? Maybe log this?
                    l = not_avail.setdefault(ns, [])
                    l.append(p)
                    continue
                l = avail.setdefault(ns, [])
                l.append(p)

        return avail, not_avail

    def _renderAvail(self, avail, resp, _props):
        re = resp.lastChild.lastChild
        re.appendChild(resp.createElement('propstat'))
        prop = resp.createElement('prop')
        re.lastChild.appendChild(prop)
        re.lastChild.appendChild(resp.createElement('status'))
        re.lastChild.lastChild.appendChild(
            resp.createTextNode('HTTP/1.1 200 OK'))
        count = 0
        for ns, props in avail.items():
            attr_name = 'a%s' % count
            if ns is not None and ns != self.default_ns:
                count += 1
                prop.setAttribute('xmlns:%s' % attr_name, ns)
            iface = _props[ns]['iface']

            if not iface:
                # The opaque properties case, hand it off
                for name in props:
                    self.oprops.renderProperty(ns, attr_name, name, prop)
                continue

            # The registered namespace case
            initial = {}
            adapted = iface(self.context)
            for name, field in getFields(iface).items():
                try:
                    value = field.get(adapted)
                except AttributeError:
                    # Interface says the attribute exists but it
                    # couldn't be found on the adapted object.
                    value = field.missing_value
                if value is not field.missing_value:
                    initial[name] = value
            setUpWidgets(self, iface, IDAVWidget, ignoreStickyValues=True,
                         initial=initial, names=initial.keys())

            for p in props:
                el = resp.createElement('%s' % p )
                if ns is not None and ns != self.default_ns:
                    el.setAttribute('xmlns', attr_name)
                prop.appendChild(el)
                widget = getattr(self, p + '_widget', None)
                if widget is None:
                    # A widget wasn't generated for this property
                    # because the attribute was missing on the adapted
                    # object, which actually means that the adapter
                    # didn't fully implement the interface ;(
                    el.appendChild(resp.createTextNode(''))
                    continue
                value = widget()

                if isinstance(value, (unicode, str)):
                    # Get the widget value here
                    el.appendChild(resp.createTextNode(value))
                else:
                    if proxy.isinstance(value, minidom.Node):
                        el.appendChild(
                            el.ownerDocument.importNode(value, True))
                    else:
                        # Try to string-ify
                        value = str(widget)
                        # Get the widget value here
                        el.appendChild(resp.createTextNode(value))

    def _renderNotAvail(self, not_avail, resp):
        re = resp.lastChild.lastChild
        re.appendChild(resp.createElement('propstat'))
        prop = resp.createElement('prop')
        re.lastChild.appendChild(prop)
        re.lastChild.appendChild(resp.createElement('status'))
        re.lastChild.lastChild.appendChild(
            resp.createTextNode('HTTP/1.1 404 Not Found'))
        count = 0
        for ns, props in not_avail.items():
            attr_name = 'a%s' % count
            if ns is not None and ns != self.default_ns:
                count += 1
                prop.setAttribute('xmlns:%s' % attr_name, ns)
            for p in props:
                el = resp.createElement('%s' % p )
                prop.appendChild(el)
                if ns is not None and ns != self.default_ns:
                    el.setAttribute('xmlns', attr_name)
