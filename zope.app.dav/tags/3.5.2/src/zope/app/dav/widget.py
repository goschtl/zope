##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Widgets specific to WebDAV

$Id$
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom

from zope.app.dav.interfaces import IDAVWidget
from zope.app.dav.interfaces import ITextDAVWidget
from zope.app.dav.interfaces import ISequenceDAVWidget
from zope.app.dav.interfaces import IXMLDAVWidget

from zope.app.form import InputWidget
from zope.interface import implements


class DAVWidget(InputWidget):

    implements(IDAVWidget)

    def hasInput(self):
        return True

    def getInputValue(self):
        return self._data

    def __call__(self):
        return unicode(self._data)

    def setRenderedValue(self, value):
        if isinstance(value, minidom.Node):
            text = u''
            for node in value.childNodes:
                if node.nodeType != node.TEXT_NODE:
                    continue
                text += node.nodeValue
            value = text

        super(DAVWidget, self).setRenderedValue(value)


class TextDAVWidget(DAVWidget):

    implements(ITextDAVWidget)


class SequenceDAVWidget(DAVWidget):

    implements(ISequenceDAVWidget)

    def __call__(self):
        return u', '.join(self._data)

    def getInputValue(self):
        return [v.strip() for v in self._data.split(',')]


class XMLDAVWidget(DAVWidget):

    implements(IXMLDAVWidget)

    def getInputValue(self):
        return self._data

    def __call__(self):
        return self._data

    def setRenderedValue(self, value):
        if not isinstance(value, minidom.Node):
            value = u''
        self._data = value
