##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
$Id: standardmacros.py,v 1.2 2003/06/06 21:35:18 philikon Exp $
"""
from zope.app.browser.skins.basic.standardmacros import StandardMacros

BaseMacros = StandardMacros

class StandardMacros(BaseMacros):
    macro_pages = ('skin_macros', 'view_macros', 'dialog_macros')
