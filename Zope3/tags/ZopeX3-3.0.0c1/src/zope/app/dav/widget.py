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

from zope.app.dav.interfaces import IDAVWidget
from zope.app.dav.interfaces import ITextDAVWidget
from zope.app.dav.interfaces import ISequenceDAVWidget

from zope.app.form.interfaces import IWidget
from zope.app.form import Widget
from zope.component.interfaces import IViewFactory
from zope.interface import implements

class DAVWidget(Widget):

    implements(IDAVWidget)

    def hasInput(self):
        return True

    def getInputValue(self):
        return self._data

    def __str__(self):
        return str(self._data)

    def __call__(self):
        return self.getInputValue()

class TextDAVWidget(DAVWidget):

    implements(ITextDAVWidget)

class SequenceDAVWidget(DAVWidget):

    implements(ISequenceDAVWidget)

    def __str__(self):
        return u', '.join(self._data)
