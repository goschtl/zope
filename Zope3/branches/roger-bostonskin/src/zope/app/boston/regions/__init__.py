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
"""Boston skin

$Id:$
"""

from zope.interface import Interface



class IHead(Interface):
    """Head region slot interface.

    This region will lookup for content providers. If you like to add 
    additional content providers to this region, use the 
    'zope.app.boston.regions.IHead' interface for the region attribute 
    in a provider directive. 
    """


class ICSS(Interface):
    """CSS region slot interface.

    This region will lookup for content providers. If you like to add 
    additional content providers to this region, use the 
    'zope.app.boston.regions.ICSS' interface for the region attribute 
    in a provider directive. 
    """


class IJavaScript(Interface):
    """Javasscript region slot interface.

    This region will lookup for content providers. If you like to add 
    additional content providers to this region, use the 
    'zope.app.boston.regions.IJavaScript' interface for the region attribute 
    in a provider directive. 
    """


class IToolBar(Interface):
    """View action region slot interface.

    This region will lookup for content providers. If you like to add 
    additional content providers to this region, use the 
    'zope.app.boston.regions.IToolBar' interface for the region attribute 
    in a provider directive.  
    """


class IContextMenu(Interface):
    """Context menu (zmi_views) region interface.

    This region will lookup for content providers. If you like to add 
    additional content providers to this region, use the 
    'zope.app.boston.regions.IContextMenu' interface for the region attribute 
    in a provider directive. 
    """


class ILeft(Interface):
    """Left region slot interface.

    This region will lookup for content providers. If you like to add 
    additional content providers to this region, use the 
    'zope.app.boston.regions.ILeft' interface for the region attribute 
    in a provider directive. 
    """
