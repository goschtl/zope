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

$Id: standardmacros.py,v 1.3 2002/12/26 20:20:48 jim Exp $
"""
from zope.app.browser.skins.basic.standardmacros import StandardMacros

ZMIMacros = StandardMacros

class StandardMacros(ZMIMacros):

    __implements__ = ZMIMacros.__implements__

    macro_pages = ('view_macros', 'widget_macros', 'dialog_macros')
