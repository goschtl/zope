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
$Id: IServiceConfiguration.py,v 1.5 2002/12/12 11:32:32 mgedmin Exp $
"""

from Interface.Attribute import Attribute
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import INamedComponentConfiguration

class IServiceConfiguration(INamedComponentConfiguration):
    """Service Configuration

    Service configurations are dependent on the components that they
    configure. They register themselves as component dependents.

    The name of a service configuration is used to determine the service
    type.
    """


__doc__ = IServiceConfiguration.__doc__ + __doc__
