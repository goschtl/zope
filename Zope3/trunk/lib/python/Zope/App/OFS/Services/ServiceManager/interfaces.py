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
"""View package.

$Id: interfaces.py,v 1.2 2002/12/19 20:38:25 jim Exp $
"""
__metaclass__ = type

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Interface import Interface
from Zope.App.ComponentArchitecture.InterfaceField import InterfaceField
from Zope.Schema import BytesLine
from Zope.ComponentArchitecture.IPresentation import IPresentation
from Zope.App.OFS.Container.IContainer import IContainer

class IViewPackageInfo(Interface):

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being viewed",
        required = True,
        )

    presentationType = InterfaceField(
        title = u"Presentation type",
        description = u"The presentation type of a view",
        required = True,
        type = IPresentation,
        default = IBrowserPresentation,
        )

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the view",
        required = True,
        )

    layer = BytesLine(
        title = u"Layer",
        description = u"The skin layer the view is registered for",
        required = False,
        min_length = 1,
        default = "default",
        )

class IViewPackage(IViewPackageInfo,  IContainer):
    """Sub-packages that contain templates that are registered as views
    """
