##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
""" Define view component for object hub.

$Id: hub.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""

from zope.app.interfaces.services.hub import IObjectHub
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView


class Control(BrowserView):
    __used_for__ = IObjectHub

    def index(self):
        return self.__control()

    __control = ViewPageTemplateFile("control.pt")
