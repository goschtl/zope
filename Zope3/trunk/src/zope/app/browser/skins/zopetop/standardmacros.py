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

$Id: standardmacros.py,v 1.4 2003/03/30 15:40:57 sidnei Exp $
"""
from zope.app.browser.skins.basic.standardmacros import StandardMacros

BaseMacros = StandardMacros

class StandardMacros(BaseMacros):

    __implements__ = BaseMacros.__implements__

    macro_pages = ('view_macros', 'widget_macros', 'dialog_macros')
