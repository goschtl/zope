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

$Id: Adder.py,v 1.2 2002/06/10 23:28:13 jim Exp $
"""

from Zope.App.OFS.Container.Views.Browser.Adder import ContainerAdder
from Zope.App.OFS.Services.AddableService import getAddableServices

class Adder(ContainerAdder):
    """Specialize addable list for service implemenations.
    """
    def _listAddables(self):
        # Override to look up from the service class registry.
        return getAddableServices(self.context)

