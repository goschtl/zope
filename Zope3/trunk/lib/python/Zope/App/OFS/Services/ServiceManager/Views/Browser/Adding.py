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
$Id: Adding.py,v 1.2 2002/07/11 18:21:32 jim Exp $
"""

from Zope.App.OFS.Container.Views.Browser.Adding import Adding as ContentAdding


class ComponentAdding(ContentAdding):
    """Adding component for service containers
    """
    
    menu_id = "add_component"

__doc__ = ComponentAdding.__doc__ + __doc__
