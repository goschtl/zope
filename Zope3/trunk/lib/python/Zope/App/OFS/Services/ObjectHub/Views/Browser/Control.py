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

$Id: Control.py,v 1.1 2002/10/30 03:47:48 poster Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.App.OFS.Services.ObjectHub.IObjectHub import IObjectHub
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class Control(BrowserView):
    __used_for__ = IObjectHub

    def index( self ):

        return self.__control()
    
    __control=ViewPageTemplateFile("control.pt")
