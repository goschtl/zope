##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

XXX - add comments into this interface.
    - extend this interface to each of the different element tree engines. So
      some example lxml supports things that the original elementtree
      implementation did and vice versa. This way developers can say give me
      an elementtree implementation support feature X. But we still need to be
      carefull that we still have a common base interface from which to work
      off.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope import interface

class IEtree(interface.Interface):

    def Comment(text = None):
        """
        """

    def dump(elem):
        """
        """

    def Element(tag, attrib = {}, **extra):
        """
        """

    def ElementTree(element = None, file = None):
        """
        """

    def XML(text):
        """
        """

    def fromstring(text):
        """
        """

    def iselement(element):
        """
        """

    def iterparse(source, events = None):
        """
        """

    def parse(source, parser = None):
        """
        """

    def PI(target, text = None):
        """
        """

    def ProcessingInstruction(target, text = None):
        """
        """

    def QName(text_or_uri, tag = None):
        """
        """

    def SubElement(parent, tag, attrib = {}, **extra):
        """
        """

    def tostring(element, encoding = None):
        """
        """

    def TreeBuilder(element_factory = None):
        """
        """

    def XMLTreeBuilder(html = 0, target = None):
        """
        """
