##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""XXX short summary goes here.

XXX longer description goes here.

$Id: xmlmetadata.py,v 1.3 2003/08/27 04:43:55 fdrake Exp $
"""

import xml.sax
import xml.sax.handler

from cStringIO import StringIO
from xml.sax.saxutils import escape, quoteattr

from zope.app.dublincore import dcterms


XSI_TYPE = (dcterms.XSI_NS, "type")

dublin_core_namespaces = dcterms.DC_NS, dcterms.DCTERMS_NS


def dumpString(mapping):
    sio = StringIO()
    nsmap = {
        # prefix: [uri, used],
        dcterms.DC_NS:      ("dc", False),
        dcterms.DCTERMS_NS: ("dcterms", False),
        dcterms.XSI_NS:     ("xsi", False),
        }
    items = mapping.items()
    items.sort()
    prev = None
    for name, values in items:
        name, type = dcterms.splitEncoding(name)
        group = name.split(".", 1)[0]
        if prev != group:
            sio.write("\n")
            prev = group
        if name in dcterms.name_to_element:
            element, t = dcterms.name_to_element[name]
            nsuri, localname = element
            if nsuri not in nsmap:
                prefix = "ns%d" % (len(nsmap) - 2)
                nsmap[nsuri] = prefix, True
            else:
                prefix, used = nsmap[nsuri]
                if not used:
                    nsmap[nsuri] = prefix, True
            qname = "%s:%s" % (prefix, localname)
            if not type:
                type = t
            if type:
                type = " xsi:type=" + quoteattr(type)
                nsmap[dcterms.XSI_NS] = "xsi", True
            for value in values:
                sio.write("  <%s%s>\n    %s\n  </%s>\n"
                          % (qname, type, _encode_string(value), qname))
        else:
            raise RuntimeError("could not serialize %r metadata element"
                               % name)
    content = sio.getvalue()
    sio = StringIO()
    sio.write("<?xml version='1.0' encoding='utf-8'?>\n"
              "<metadata")
    for uri, (prefix, used) in nsmap.iteritems():
        if used:
            sio.write("\n  xmlns:%s=%s" % (prefix, quoteattr(uri)))
    sio.write(">\n")
    sio.write(content)
    sio.write("</metadata>\n")
    return sio.getvalue()

try:
    unicode
except NameError:
    _encode_string = escape
else:
    def _encode_string(s):
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        return escape(s)


def parse(source, error_handler=None):
    parser, ch = _setup_parser(error_handler)
    parser.parse(source)
    return ch.mapping

def parseString(text, error_handler=None):
    parser, ch = _setup_parser(error_handler)
    parser.feed(text)
    parser.close()
    return ch.mapping

def _setup_parser(error_handler):
    parser = xml.sax.make_parser()
    ch = DublinCoreHandler()
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    parser.setContentHandler(ch)
    if error_handler is not None:
        parser.setErrorHandler(error_handler)
    return parser, ch


class PrefixManager:
    # We don't use this other than in the DublinCoreHandler, but it's
    # entirely general so we'll separate it out for now.

    """General handler for namespace prefixes.

    This should be used as a mix-in when creating a ContentHandler.
    """

    __prefix_map = None

    def startPrefixMapping(self, prefix, uri):
        if self.__prefix_map is None:
            self.__prefix_map = {}
        pm = self.__prefix_map
        pm.setdefault(prefix, []).append(uri)

    def endPrefixMapping(self, prefix):
        pm = self.__prefix_map
        uris = pm[prefix]
        del uris[-1]
        if not uris:
            del pm[prefix]

    def get_uri(self, prefix):
        pm = self.__prefix_map
        if pm is None:
            return None
        if prefix in pm:
            return pm[prefix][-1]
        else:
            return None


class DublinCoreHandler(PrefixManager, xml.sax.handler.ContentHandler):

    def startDocument(self):
        self.mapping = {}
        self.stack = []

    def get_dc_container(self):
        name = None
        for (uri, localname), dcelem, validator in self.stack:
            if uri in dublin_core_namespaces:
                name = uri, localname
        if name in dcterms.element_to_name:
            # dcelem contains type info, so go back to the mapping
            return dcterms.element_to_name[name]
        else:
            return None

    def startElementNS(self, name, qname, attrs):
        self.buffer = u""
        # XXX need convert element to metadata element name
        dcelem = validator = None
        if name in dcterms.element_to_name:
            dcelem = dcterms.element_to_name[name]
        type = attrs.get(XSI_TYPE)
        if type:
            if not dcelem:
                raise ValueError(
                    "data type specified for unknown metadata element: %s"
                    % qname)
            if ":" in type:
                prefix, t = type.split(":", 1)
                ns = self.get_uri(prefix)
                if ns != dcterms.DCTERMS_NS:
                    raise ValueError("unknown data type namespace: %s" % t)
                type = t
            if type not in dcterms.encodings:
                raise ValueError("unknown data type: %r" % type)
            allowed_in, validator = dcterms.encodings[type]
            if dcelem not in allowed_in:
                raise ValueError("%s values are not allowed for %r"
                                 % (type, dcelem))
            dcelem = "%s.%s" % (dcelem, type)
        if dcelem:
            cont = self.get_dc_container()
            if cont and cont != dcelem:
                prefix = cont + "."
                if not dcelem.startswith(prefix):
                    raise ValueError("%s is not a valid refinement for %s"
                                     % (dcelem, cont))
        self.stack.append((name, dcelem, validator))

    def endElementNS(self, name, qname):
        startname, dcelem, validator = self.stack.pop()
        assert startname == name
        if self.buffer is None:
            return
        data = self.buffer.strip()
        self.buffer = None
        if not dcelem:
            return
        if validator is not None:
            validator(data)
        if dcelem in self.mapping:
            self.mapping[dcelem] += (data,)
        else:
            self.mapping[dcelem] = (data,)

    def characters(self, data):
        if self.buffer is not None:
            self.buffer += data
