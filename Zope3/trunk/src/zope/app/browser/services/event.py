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
""" Define view component for event service control.

$Id: event.py,v 1.3 2002/12/30 14:02:54 stevea Exp $
"""

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.interfaces.services.event import IEventService
from zope.publisher.browser import BrowserView


class Control(BrowserView):
    __used_for__ = IEventService

    def index(self):
        return self.__control()

    __control = ViewPageTemplateFile("eventcontrol.pt")
