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

$Id: StandardMacros.py,v 1.1 2002/10/23 15:02:29 sidnei Exp $
"""
from Zope.App.ZMI.ZMIViewUtility import ZMIViewUtility
from Zope.App.PageTemplate.ViewPageTemplateFile import ViewPageTemplateFile
from Zope.App.ZMI.StandardMacros import Macros

class StandardMacros(ZMIViewUtility, Macros):

    __implements__ = ZMIViewUtility.__implements__

    macro_pages = (
            ViewPageTemplateFile('www/view_macros.pt'), 
            ViewPageTemplateFile('www/widget_macros.pt'),
            ViewPageTemplateFile('www/dialog_macros.pt')
            )

