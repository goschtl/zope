##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Zope Element Tree Support

$Id$
"""
__docformat__ = 'restructuredtext'

import copy
from zope.interface import implements

from interfaces import IEtree

class BaseEtree(object):
    def Comment(self, text = None):
        return self.etree.Comment(text)

    # XXX - not tested
    def dump(self, elem):
        return self.etree.dump(elem)

    def Element(self, tag, attrib = {}, **extra):
        return self.etree.Element(tag, attrib, **extra)

    def ElementTree(self, element = None, file = None):
        return self.etree.ElementTree(element, file)

    def XML(self, text):
        return self.etree.fromstring(text)

    fromstring = XML

    def iselement(self, element):
        return self.etree.iselement(element)

    # XXX - not tested
    def iterparse(self, source, events = None):
        return self.etree.iterparse(source, events)

    def parse(self, source, parser = None):
        return self.etree.parse(source, parser)

    def PI(self, target, text = None):
        raise NotImplementedError, "lxml doesn't implement PI"

    ProcessingInstruction = PI

    def QName(self, text_or_uri, tag = None):
        return self.etree.QName(text_or_uri, tag)

    def SubElement(self, parent, tag, attrib = {}, **extra):
        return self.etree.SubElement(parent, tag, attrib, **extra)

    def tostring(self, element, encoding = None):
        return self.etree.tostring(element, encoding)

    def TreeBuilder(self, element_factory = None):
        raise NotImplementedError, "lxml doesn't implement TreeBuilder"

    def XMLTreeBuilder(self, html = 0, target = None):
        raise NotImplementedError, "lxml doesn't implement XMLTreeBuilder"


class EtreeEtree(BaseEtree):
    """
    Support for ElementTree

      >>> from cStringIO import StringIO
      >>> from zope.interface.verify import verifyObject
      >>> letree = EtreeEtree()
      >>> verifyObject(IEtree, letree)
      True

      >>> letree.Comment(u'some text') #doctest:+ELLIPSIS
      <Element <function Comment at ...

      >>> letree.Element(u'testtag')
      <Element...

      >>> letree.ElementTree() #doctest:+ELLIPSIS
      <elementtree.ElementTree.ElementTree instance at ...

      >>> letree.XML(u'<p>some text</p>')
      <Element p ...

      >>> letree.fromstring(u'<p>some text</p>')
      <Element p ...

      >>> elem = letree.Element(u'testtag')
      >>> letree.iselement(elem)
      1

      >>> f = StringIO('<b>Test Source String</b>')
      >>> letree.parse(f) #doctest:+ELLIPSIS
      <elementtree.ElementTree.ElementTree instance at ...

      >>> letree.QName('http://example.namespace.org', 'test')#doctest:+ELLIPSIS
      <elementtree.ElementTree.QName instance at...

      >>> print letree.tostring(elem, 'ascii')
      <?xml version='1.0' encoding='ascii'?>
      <testtag />

      >>> letree.TreeBuilder()
      Traceback (most recent call last):
      ...
      NotImplementedError: lxml doesn't implement TreeBuilder

      >>> subel = letree.SubElement(elem, 'foo')
      >>> letree.tostring(elem)
      '<testtag><foo /></testtag>'

      >>> letree.PI('sometarget')  #doctest:+ELLIPSIS
      <Element <function ProcessingInstruction at ...

      >>> letree.ProcessingInstruction('sometarget') #doctest:+ELLIPSIS
      <Element <function ProcessingInstruction at ...

      >>> letree.XMLTreeBuilder()
      <elementtree.ElementTree.XMLTreeBuilder instance at ...

    """
    implements(IEtree)

    def __init__(self):
        from elementtree import ElementTree
        self.etree = ElementTree

    def XMLTreeBuilder(self, html = 0, target = None):
        return self.etree.XMLTreeBuilder(html, target)

    def PI(self, target, text = None):
        return self.etree.PI(target, text)

    ProcessingInstruction = PI


class EtreePy25(BaseEtree):
    """
    Support for ElementTree

      >>> from cStringIO import StringIO
      >>> from zope.interface.verify import verifyObject
      >>> letree = EtreePy25()
      >>> verifyObject(IEtree, letree)
      True

      >>> letree.Comment(u'some text') #doctest:+ELLIPSIS
      <Element <function Comment at ...

      >>> letree.Element(u'testtag')
      <Element...

      >>> letree.ElementTree() #doctest:+ELLIPSIS
      <xml.etree.ElementTree.ElementTree instance at ...

      >>> letree.XML(u'<p>some text</p>')
      <Element p ...

      >>> letree.fromstring(u'<p>some text</p>')
      <Element p ...

      >>> elem = letree.Element(u'testtag')
      >>> letree.iselement(elem)
      1

      >>> f = StringIO('<b>Test Source String</b>')
      >>> letree.parse(f) #doctest:+ELLIPSIS
      <xml.etree.ElementTree.ElementTree instance at ...

      >>> letree.QName('http://example.namespace.org', 'test')#doctest:+ELLIPSIS
      <xml.etree.ElementTree.QName instance at...

      >>> print letree.tostring(elem, 'ascii')
      <?xml version='1.0' encoding='ascii'?>
      <testtag />

      >>> letree.TreeBuilder()
      Traceback (most recent call last):
      ...
      NotImplementedError: lxml doesn't implement TreeBuilder

      >>> subel = letree.SubElement(elem, 'foo')
      >>> letree.tostring(elem)
      '<testtag><foo /></testtag>'

      >>> letree.PI('sometarget')  #doctest:+ELLIPSIS
      <Element <function ProcessingInstruction at ...

      >>> letree.ProcessingInstruction('sometarget') #doctest:+ELLIPSIS
      <Element <function ProcessingInstruction at ...

      >>> letree.XMLTreeBuilder()
      <xml.etree.ElementTree.XMLTreeBuilder instance at ...

    """
    implements(IEtree)

    def __init__(self):
        from xml.etree import ElementTree
        self.etree = ElementTree

    def XMLTreeBuilder(self, html = 0, target = None):
        return self.etree.XMLTreeBuilder(html, target)

    def PI(self, target, text = None):
        return self.etree.PI(target, text)

    ProcessingInstruction = PI


class LxmlEtree(BaseEtree):
    """
    Support for lxml.

      >>> from cStringIO import StringIO
      >>> from zope.interface.verify import verifyObject
      >>> letree = LxmlEtree()
      >>> verifyObject(IEtree, letree)
      True

      >>> letree.Comment(u'some text')
      <Comment[some text]>

      >>> letree.Element(u'testtag')
      <Element...

      >>> letree.ElementTree()
      <etree._ElementTree...

      >>> letree.XML(u'<p>some text</p>')
      <Element p ...

      >>> letree.fromstring(u'<p>some text</p>')
      <Element p ...

    When we have a element whoes namespace declaration is declared in a parent
    element lxml doesn't print out the namespace declaration by default.

      >>> multinselemstr = '<D:prop xmlns:D="DAV:"><D:owner><H:href xmlns:H="examplens">http://example.org</H:href></D:owner></D:prop>'
      >>> multinselem = letree.fromstring(multinselemstr)
      >>> letree.tostring(multinselem[0])
      '<D:owner xmlns:D="DAV:"><H:href xmlns:H="examplens">http://example.org</H:href></D:owner>'

      >>> elem = letree.Element(u'testtag')
      >>> letree.iselement(elem)
      1

      >>> f = StringIO('<b>Test Source String</b>')
      >>> letree.parse(f)
      <etree._ElementTree object at ...

      >>> letree.QName('http://example.namespace.org', 'test')
      <etree.QName object at...

      >>> letree.tostring(elem, 'ascii')
      '<testtag/>'

      >>> letree.TreeBuilder()
      Traceback (most recent call last):
      ...
      NotImplementedError: lxml doesn't implement TreeBuilder

      >>> subel = letree.SubElement(elem, 'foo')
      >>> subel.getparent() is elem
      True

      >>> letree.PI('sometarget')
      Traceback (most recent call last):
      ...
      NotImplementedError: lxml doesn't implement PI

      >>> letree.ProcessingInstruction('sometarget')
      Traceback (most recent call last):
      ...
      NotImplementedError: lxml doesn't implement PI

      >>> letree.XMLTreeBuilder()
      Traceback (most recent call last):
      ...
      NotImplementedError: lxml doesn't implement XMLTreeBuilder

    """
    implements(IEtree)

    def __init__(self):
        from lxml import etree
        self.etree = etree

    def tostring(self, element, encoding = None):
        """LXML loses the namespace information whenever we print out an
        element who namespace was defined in 
        """
        return self.etree.tostring(copy.copy(element), encoding)
