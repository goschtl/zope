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
$Id: IServiceConfiguration.py,v 1.3 2002/12/03 18:15:30 efge Exp $
"""

from Interface.Attribute import Attribute
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfiguration

class IServiceConfiguration(IConfiguration):
    """Service Configuration

    Service configurations are dependent on the components that they
    configure. They register themselves as component dependents.
    
    """

    serviceType = Attribute("The service type id")

    componentPath = Attribute("The physical path to the component")

    def getService():
        """Return the service component named in the directive.
        """

__doc__ = IServiceConfiguration.__doc__ + __doc__

