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

from zope.contentprovider.interfaces import IRegion



class IHead(IRegion):
    """Head pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IHead' 
    interface for the slot attribute in a pagelet directive.
    """


class ICSS(IRegion):
    """CSS pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.ICSS' 
    interface for the slot attribute in a pagelet directive.
    """


class IJavaScript(IRegion):
    """Javasscript pagelet slot interface. 

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IJavaScript' 
    interface for the slot attribute in a pagelet directive. 
    """


class IToolBar(IRegion):
    """View action pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IToolBar' 
    interface for the slot attribute in a pagelet directive. 
    """


class IContextMenu(IRegion):
    """Context menu (zmi_views) pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IContextMenu' 
    interface for the slot attribute in a pagelet directive. 
    """


class ILeft(IRegion):
    """Left pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.ILeft' 
    interface for the slot attribute in a pagelet directive.
    """
