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
$Id: IServiceDirective.py,v 1.1 2002/07/11 18:21:32 jim Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute

class IServiceDirective(Interface):
    """Service Configuration Directives
    """

    service_type = Attribute("The service type id")
    component_path = Attribute("The physical path to the component")

    def getService(service_manager):
        """Return the service component named in the directive.
        """

__doc__ = IServiceDirective.__doc__ + __doc__

