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

$Id: Control.py,v 1.2 2002/06/10 23:28:11 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.Event.IEventService import IEventService
from Zope.PageTemplate.PageTemplateFile import PageTemplateFile
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class Control(BrowserView):
    __used_for__ = IEventService

    def index( self, toggleSubscribeOnBind=0, REQUEST=None):
        if toggleSubscribeOnBind:
            cntx=removeAllProxies(self.context)
            cntx.subscribeOnBind=not cntx.subscribeOnBind
        return self.__control(REQUEST)
    
    __control=PageTemplateFile("control.pt")
