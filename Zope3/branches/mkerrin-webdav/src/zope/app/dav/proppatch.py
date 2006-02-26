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

import transaction
from zope import component
from zope.app.container.interfaces import IReadContainer
from zope.app.traversing.browser.absoluteurl import absoluteURL

from common import MultiStatus
from common import DAVError, UnprocessableEntityError, ForbiddenError
from interfaces import INamespaceManager, INamespaceRegistry


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
        if self.content_type not in ('text/xml', 'application/xml'):
            self.request.response.setStatus(400)
            return ''

        resource_url = absoluteURL(self.context, self.request)
        if IReadContainer.providedBy(self.context):
            resource_url += '/'

        xmldoc = minidom.parse(self.request.bodyStream)

        responsedoc = MultiStatus()
        propertyupdate = xmldoc.documentElement
        if propertyupdate.namespaceURI != self.default_ns or \
               propertyupdate.localName != 'propertyupdate':
            self.request.response.setStatus(422)
            return ''

        try:
            self._handlePropertyUpdate(responsedoc, propertyupdate)
        except DAVError, error:
            self.request.response.setStatus(error.status)
            return ''

        body = responsedoc.body.toxml('utf-8')
        self.request.response.setResult(body)
        self.request.response.setStatus(207)
        return body

    def _handlePropertyUpdate(self, responsedoc, source):
        _propresults = {}

        nr = component.getUtility(INamespaceRegistry, context = self.context)

        for update in source.childNodes:
            if update.nodeType != update.ELEMENT_NODE:
                continue
            if update.localName not in ('set', 'remove'):
                continue

            props = update.getElementsByTagNameNS(self.default_ns, 'prop')
            if not props:
                continue

            for prop in props[0].childNodes:
                if not prop.nodeType == prop.ELEMENT_NODE:
                    continue

                namespace = prop.namespaceURI

                nsmanager = nr.getNamespaceManager(namespace)
                if nsmanager is None:
                    raise ForbiddenError(prop.localName,
                                       "namespace %s doesn't exist" % namespace)

                if update.localName == 'set':
                    status = self._handleSet(nsmanager, prop)
                else:
                    status = self._handleRemove(nsmanager, prop)

                results = _propresults.setdefault(status, {})
                props = results.setdefault(namespace, [])
                if prop.localName not in props:
                    props.append(prop.localName)

        if not _propresults:
            raise UnprocessableEntityError(None, "")

        if _propresults.keys() != [200]:
            transaction.abort()
            # Move 200 succeeded props to the 424 status
            if _propresults.has_key(200):
                failed = _propresults.setdefault(424, {})
                for ns, props in _propresults[200].items():
                    failed_props = failed.setdefault(ns, [])
                    failed_props.extend(props)
                del _propresults[200]

        renderedns  = {}
        count = 0
        resp = responsedoc.addResponse(self.context, self.request)
        for status, namespaces in _propresults.items():
            for namespace, properties in namespaces.items():
                if renderedns.has_key(namespace):
                    ns_prefix = renderedns[namespace]
                elif namespace != self.default_ns:
                    ns_prefix = renderedns[namespace] = 'a%s' % count
                    count += 1
                else: # default_ns
                    ns_prefix = renderedns[namespace] = None

                for propname in properties:
                    el = resp.createEmptyElement(namespace, ns_prefix,
                                                 propname)
                    resp.addPropertyByStatus(namespace, ns_prefix, el, status)

    def _handleSet(self, nsmanager, prop):
        propname = prop.localName

        # we can't add a property to a live namespace - forbidden
        if nsmanager.isLiveNamespace() and \
               nsmanager.queryProperty(self.context, propname, None) is None:
            return 403

        # we aren't rendereding the property so setting ns_prefix to None is ok
        widget = nsmanager.getWidget(self.context, self.request,
                                     propname, None)
        field = nsmanager.getProperty(self.context, propname)

        if field.readonly:
            # XXX - RFC 2518 specifies 409 for readonly props but the next
            # version of the spec says it is 403 since it isn't allowed.
            return 409

        widget.setProperty(prop)

        if not widget.hasValidInput():
            return 409 # Didn't match the field validation

        if widget.applyChanges(field.context):
            return 200

        return 422 # Field didn't accept the value - is the correct value.

    def _handleRemove(self, nsmanager, prop):
        # XXX - should the INamespaceManager utility be managing the removal
        # of properties at this level.
        try:
            nsmanager.removeProperty(self.context, prop.localName)
        except DAVError, error:
            return error.status

        return 200
