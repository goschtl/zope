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

$Id: StandardMacros.py,v 1.2 2002/10/22 19:34:59 stevea Exp $
"""
from ZMIViewUtility import ZMIViewUtility
from Zope.App.PageTemplate.ViewPageTemplateFile import ViewPageTemplateFile

class Macros:

    macro_pages = ()

    def __getitem__(self, key):
        for page in self.macro_pages:
            v = page.macros.get(key)
            if v is not None:
                return v
        raise KeyError, key

class StandardMacros(ZMIViewUtility, Macros):

    __implements__ = ZMIViewUtility.__implements__

    macro_pages = (
            ViewPageTemplateFile('www/view_macros.pt'),
            ViewPageTemplateFile('www/dialog_macros.pt')
            )

