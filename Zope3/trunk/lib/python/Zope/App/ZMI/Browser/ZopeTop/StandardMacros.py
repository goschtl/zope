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
"""Standard macros for page templates in the ZMI

The macros are drawn from various different page templates.

$Id: StandardMacros.py,v 1.2 2002/10/31 13:19:17 stevea Exp $
"""
from Zope.App.ZMI.StandardMacros import StandardMacros as ZMIMacros

class StandardMacros(ZMIMacros):

    __implements__ = ZMIMacros.__implements__

    macro_pages = ('view_macros', 'widget_macros', 'dialog_macros')

