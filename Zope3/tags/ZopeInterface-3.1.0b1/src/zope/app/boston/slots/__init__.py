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

$Id$
"""

from zope.app.pagelet.interfaces import IPageletSlot



class IHead(IPageletSlot):
    """Head pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IHead' 
    interface for the slot attribute in a pagelet directive.
    """


class ICSS(IPageletSlot):
    """CSS pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IHead' 
    interface for the slot attribute in a pagelet directive.
    """


class IJavaScript(IPageletSlot):
    """Javasscript pagelet slot interface. 

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IJavaScript' 
    interface for the slot attribute in a pagelet directive. 
    """


class IToolBar(IPageletSlot):
    """View action pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IViewAction' 
    interface for the slot attribute in a pagelet directive. 
    """


class IContextMenu(IPageletSlot):
    """Context menu (zmi_views) pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.IContextMenu' 
    interface for the slot attribute in a pagelet directive. 
    """


class ILeft(IPageletSlot):
    """Left pagelet slot interface.

    This pagelet slot will lookup for pagelets. If you like to additional 
    content to this slot, use the 'zope.app.boston.slots.ILeft' 
    interface for the slot attribute in a pagelet directive.
    """
