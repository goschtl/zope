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
$Id: standardmacros.py,v 1.2 2004/03/23 22:08:28 srichter Exp $
"""
from zope.app.basicskin.standardmacros import StandardMacros as BaseMacros

class StandardMacros(BaseMacros):
    macro_pages = ('skin_macros', 'view_macros', 'dialog_macros',
                   'navigation_macros')
    
    aliases = {'view': 'page', 'dialog': 'page', 'addingdialog': 'page'}
