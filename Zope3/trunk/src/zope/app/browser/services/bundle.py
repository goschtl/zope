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
"""Bundle support.

(See also http://dev.zope.org/Zope3/ThroughTheWebSiteDevelopment .)

A (site-management) bundle is a (site-management) folder with special
status.

Eventually, bundles will be read-only, and the only thing you can do
with bundles is install and uninstall them.  At installation time, a
bundle's dependencies and are analized and satisfied, and the
configurations in the bundle are activated, unless they conflict with
existing configurations.  This is an interactive process.

XXX This interim code is much less ambitious: it just provides a view
on a (site-management) folder that displays all configurations in a
bundle and lets the user activate them.

$Id: bundle.py,v 1.1 2003/06/16 16:00:37 gvanrossum Exp $
"""

from zope.app import zapi
from zope.publisher.browser import BrowserView
from zope.app.interfaces.container import IReadContainer
from zope.app.interfaces.services.folder import ISiteManagementFolder
from zope.app.interfaces.services.configuration import IConfigurationManager
from zope.app.interfaces.services.configuration import IConfiguration
from zope.proxy import removeAllProxies

class BundleView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.configurations = self.findConfigurations(self.context, "")
        self.configurations.sort(self.compareConfigurations)
        self.services = self.find_services()

    # Methods called from the page template (bundle.pt)

    def listServices(self):
        infos = []
        for name in self.services:
            svc = zapi.getService(self.context, name)
            path = zapi.getPath(svc)
            d = {"service": name, "path": path}
            infos.append(d)
        return infos

    def listConfigurations(self):
        infos = []
        for path, obj in self.configurations:
            d = {"path": path,
                 "service": self.getServiceName(obj),
                 "status": obj.status,
                 "usage": obj.usageSummary(),
                 "implementation": obj.implementationSummary()}
            infos.append(d)
        return infos

    # The rest are helper methods

    def findConfigurations(self, f, prefix):
        alist = []
        for name, obj in f.items():
            if IConfiguration.isImplementedBy(obj):
                alist.append((prefix+name, obj))
            elif IReadContainer.isImplementedBy(obj):
                alist.extend(self.findConfigurations(obj, prefix+name+"/"))
        return alist

    def compareConfigurations(self, c1, c2):
        path1, obj1 = c1
        path2, obj2 = c2
        t1 = (self.getServiceName(obj1),
              obj1.usageSummary(),
              obj1.implementationSummary())
        t2 = (self.getServiceName(obj2),
              obj2.usageSummary(),
              obj2.implementationSummary())
        return cmp(t1, t2)

    def find_services(self):
        sd = {}
        for path, obj in self.configurations:
            sd[self.getServiceName(obj)] = 1
        services = sd.keys()
        services.sort()
        return services

    def getServiceName(self, configuration):
        # Return the service associated with a configuration.

        # XXX There is no public API to get this information; while I
        # ponder how to define such an API, I use a hack: all current
        # configuration implementations use the
        # ConfigurationStatusProperty class, and it stores the service
        # name on its 'service' attribute.  We can get to this via the
        # class.
        configuration = removeAllProxies(configuration)
        return configuration.__class__.status.service
