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
$Id: IServiceConfiguration.py,v 1.4 2002/12/05 17:00:44 jim Exp $
"""

from Interface.Attribute import Attribute
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import IComponentConfiguration

class IServiceConfiguration(IComponentConfiguration):
    """Service Configuration

    Service configurations are dependent on the components that they
    configure. They register themselves as component dependents.
    
    """

    serviceType = Attribute("The service type id")

__doc__ = IServiceConfiguration.__doc__ + __doc__

