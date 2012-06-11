##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""DAV Opaque properties implementation details

Opaque properties are arbitrary propterties set trhough DAV and which have no
special meaning to the Zope application.

$Id$
"""
__docformat__ = 'restructuredtext'

from UserDict import DictMixin
from xml.dom import minidom

from zope.interface import implements
from zope.interface.common.mapping import IMapping
from zope.location import Location
from zope.annotation.interfaces import IAnnotations, IAnnotatable

from BTrees.OOBTree import OOBTree

DANkey = "zope.app.dav.DAVOpaqueProperties"


class IDAVOpaqueNamespaces(IMapping):
    """Opaque storage for non-registered DAV namespace properties.

    Any unknown (no interface registered) DAV properties are stored opaquely
    keyed on their namespace URI, so we can return them later when requested.
    Thus this is a mapping of a mapping. 
    
    """
    
    def renderProperty(ns, nsprefix, prop, propel):
        """Render the named property to a DOM subtree
        
        ns and prop are keys defining the property, nsprefix is the namespace
        prefix used in the DOM for the namespace of the property, and propel
        is the <prop> element in the target DOM to which the property DOM 
        elements need to be added.
        
        """
        
    def setProperty(propel):
        """Store a DOM property in the opaque storage
        
        propel is expected to be a DOM element from which the namespace and
        property name are taken to be stored.
        
        """
        
    def removeProperty(ns, prop):
        """Remove the indicated property altogether"""

    
class DAVOpaqueNamespacesAdapter(DictMixin, Location):
    """Adapt annotatable objects to DAV opaque property storage."""
    
    implements(IDAVOpaqueNamespaces)
    __used_for__ = IAnnotatable

    annotations = None

    def __init__(self, context):
        annotations = IAnnotations(context)
        oprops = annotations.get(DANkey)
        if oprops is None:
            self.annotations = annotations
            oprops = OOBTree()

        self._mapping = oprops
        
    def _changed(self):
        if self.annotations is not None:
            self.annotations[DANkey] = self._mapping
            self.annotations = None

    def get(self, key, default=None):
        return self._mapping.get(key, default)

    def __getitem__(self, key):
        return self._mapping[key]
        
    def keys(self):
        return self._mapping.keys()
    
    def __setitem__(self, key, value):
        self._mapping[key] = value
        self._changed()

    def __delitem__(self, key):
        del self._mapping[key]
        self._changed()
    
    #
    # Convenience methods; storing and retrieving properties through WebDAV
    # It may be better to use specialised IDAWWidget implementatins for this.
    #
    def renderProperty(self, ns, nsprefix, prop, propel):
        """Render a property as DOM elements"""
        value = self.get(ns, {}).get(prop)
        if value is None:
            return
        value = minidom.parseString(value)
        el = propel.ownerDocument.importNode(value.documentElement, True)
        el.setAttribute('xmlns', nsprefix)
        propel.appendChild(el)

    def setProperty(self, propel):
        ns = propel.namespaceURI
        props = self.setdefault(ns, OOBTree())
        propel = makeDOMStandalone(propel)
        props[propel.nodeName] = propel.toxml('utf-8')
        
    def removeProperty(self, ns, prop):
        if self.get(ns, {}).get(prop) is None:
            return
        del self[ns][prop]
        if not self[ns]:
            del self[ns]


def makeDOMStandalone(element):
    """Make a DOM Element Node standalone
    
    The DOM tree starting at element is copied to a new DOM tree where:
        
    - Any prefix used for the element namespace is removed from the element 
      and all attributes and decendant nodes.
    - Any other namespaces used on in the DOM tree is explcitly declared on
      the root element.
      
    So, if the root element to be transformed is defined with a prefix, that 
    prefix is removed from the whole tree:
        
      >>> dom = minidom.parseString('''<?xml version="1.0"?>
      ...      <foo xmlns:bar="http://bar.com">
      ...         <bar:spam><bar:eggs /></bar:spam>
      ...      </foo>''')
      >>> element = dom.documentElement.getElementsByTagName('bar:spam')[0]
      >>> standalone = makeDOMStandalone(element)
      >>> standalone.toxml()
      u'<spam><eggs/></spam>'
      
    Prefixes are of course also removed from attributes:
        
      >>> element.setAttributeNS(element.namespaceURI, 'bar:vikings', 
      ...                        'singing')
      >>> standalone = makeDOMStandalone(element)
      >>> standalone.toxml()
      u'<spam vikings="singing"><eggs/></spam>'
      
    Any other namespace used will be preserved, with the prefix definitions
    for these renamed and moved to the root element:
      
      >>> dom = minidom.parseString('''<?xml version="1.0"?>
      ...      <foo xmlns:bar="http://bar.com" xmlns:mp="uri://montypython">
      ...         <bar:spam>
      ...           <bar:eggs mp:song="vikings" />
      ...           <mp:holygrail xmlns:c="uri://castle">
      ...             <c:camelot place="silly" />
      ...           </mp:holygrail>
      ...           <lancelot xmlns="uri://montypython" />
      ...         </bar:spam>
      ...      </foo>''')
      >>> element = dom.documentElement.getElementsByTagName('bar:spam')[0]
      >>> standalone = makeDOMStandalone(element)
      >>> print standalone.toxml()
      <spam xmlns:p0="uri://montypython" xmlns:p1="uri://castle">
                <eggs p0:song="vikings"/>
                <p0:holygrail>
                  <p1:camelot place="silly"/>
                </p0:holygrail>
                <p0:lancelot/>
              </spam>
    """
    
    return DOMTransformer(element).makeStandalone()


def _numberGenerator(i=0):
    while True:
        yield i
        i += 1


class DOMTransformer(object):
    def __init__(self, el):
        self.source = el
        self.ns = el.namespaceURI
        self.prefix = el.prefix
        self.doc = minidom.getDOMImplementation().createDocument(
            self.ns, el.localName, None)
        self.dest = self.doc.documentElement
        self.prefixes = {}
        self._seq = _numberGenerator()
        
    def seq(self): return self._seq.next()
    seq = property(seq)
    
    def _prefixForURI(self, uri):
        if not uri or uri == self.ns:
            return ''
        if not self.prefixes.has_key(uri):
            self.prefixes[uri] = 'p%d' % self.seq
        return self.prefixes[uri] + ':'

    def makeStandalone(self):
        self._copyElement(self.source, self.dest)
        for ns, prefix in self.prefixes.items():
            self.dest.setAttribute('xmlns:%s' % prefix, ns)
        return self.dest

    def _copyElement(self, source, dest):
        for i in range(source.attributes.length):
            attr = source.attributes.item(i)
            if attr.prefix == 'xmlns' or attr.nodeName == 'xmlns':
                continue
            ns = attr.prefix and attr.namespaceURI or source.namespaceURI
            qname = attr.localName
            if ns != dest.namespaceURI:
                qname = '%s%s' % (self._prefixForURI(ns), qname)
            dest.setAttributeNS(ns, qname, attr.value)

        for node in source.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                ns = node.namespaceURI
                qname = '%s%s' % (self._prefixForURI(ns), node.localName)
                copy = self.doc.createElementNS(ns, qname)
                self._copyElement(node, copy)
            else:
                copy = self.doc.importNode(node, True)
            dest.appendChild(copy)
