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

$Id: Services.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getView

class Services(BrowserView):

    def update(self):

        service_types = list(self.context.getBoundServiceTypes())
        service_types.sort()

        services = []
        for service_type in service_types:
            registry = self.context.queryConfigurations(service_type)
            view = getView(registry, "ChangeConfigurations", self.request)
            view.setPrefix(service_type)
            view.update()
            active = registry.active() is not None
            services.append(
                {"name": service_type,
                 "active": active,
                 "inactive": not active,
                 "view": view,
                 })

        return services
    
