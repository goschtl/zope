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
$Id: Adding.py,v 1.1 2002/06/24 16:18:50 srichter Exp $
"""

from Zope.App.OFS.Container.Views.Browser.Adding import Adding as ContentAdding

class ConnectionAdding(ContentAdding):
    """Adding component for service containers
    """
    
    menu_id = "add_connection"

__doc__ = ConnectionAdding.__doc__ + __doc__
