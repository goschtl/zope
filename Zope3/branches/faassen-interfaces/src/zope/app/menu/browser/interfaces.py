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
"""
$Id: interfaces.py,v 1.1 2004/03/10 23:10:44 srichter Exp $
"""
from zope.interface import Interface

class IMenuAccessView(Interface):
    """View that provides access to menus"""

    def __getitem__(menu_id):
        """Get menu information

        Return a sequence of dictionaries with labels and
        actions, where actions are relative URLs.
        """
