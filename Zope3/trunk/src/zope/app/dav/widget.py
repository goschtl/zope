##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Widgets specific to WebDAV

$Id: widget.py,v 1.3 2003/06/03 22:46:19 jim Exp $
"""

from zope.app.interfaces.dav import ISimpleDAVWidget
from zope.app.interfaces.form import IWidget
from zope.component.interfaces import IViewFactory
from zope.app.form.widget import Widget

class SimpleDAVWidget(Widget):
    __implements__ = (ISimpleDAVWidget, IWidget, IViewFactory)

    def haveData(self):
        return 1

    def getData(self):
        return self._data

    def __str__(self):
        return str(self._data)

    def __call__(self):
        return self.getData()

class TextDAVWidget(SimpleDAVWidget):
    pass

class SequenceDAVWidget(SimpleDAVWidget):

    def __str__(self):
        return u', '.join(self._data)
