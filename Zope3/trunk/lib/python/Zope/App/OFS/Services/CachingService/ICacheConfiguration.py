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
"""A configuration for a cache.

$Id: ICacheConfiguration.py,v 1.1 2002/12/12 15:28:16 mgedmin Exp $
"""

from Zope.App.OFS.Services.ConfigurationInterfaces \
     import INamedComponentConfiguration

class ICacheConfiguration(INamedComponentConfiguration):
    """Cache configuration

    Cache configurations are dependent on the caches that they configure. They
    register themselves as component dependents.
    """
