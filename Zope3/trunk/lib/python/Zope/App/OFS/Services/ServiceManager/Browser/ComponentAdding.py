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

$Id: ComponentAdding.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from Zope.App.OFS.Container.Views.Browser.Adding import Adding
from Zope.App.OFS.Services.ServiceManager.IServiceAdding import IServiceAdding

class ServiceAdding(Adding):
    
    __implements__ = IServiceAdding

