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
"""

$Id: Widget.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""
from IWidget import IWidget

class Widget:
    """I do not know what will be in this class, but it provides
    an extra layer.
    """

    __implements__ = IWidget

    propertyNames = []


    def __init__(self, field):
        """ """
        self.context = field


    def getValue(self, name):
        """ """
        if name in self.propertyNames:
            return getattr(self, name, None)
