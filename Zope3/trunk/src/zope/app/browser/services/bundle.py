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

$Id: bundle.py,v 1.5 2003/06/17 01:53:47 gvanrossum Exp $
"""

from transaction import get_transaction
from zope.app import zapi
from zope.app.interfaces.container import IReadContainer
from zope.app.interfaces.services.configuration import IConfiguration
from zope.app.interfaces.services.configuration import IConfigurationManager
from zope.app.interfaces.services.configuration import Active, Registered
from zope.app.interfaces.services.configuration import Unregistered
from zope.app.interfaces.services.folder import ISiteManagementFolder
from zope.app.interfaces.services.service import IServiceConfiguration
from zope.component import ComponentLookupError
from zope.proxy import removeAllProxies
from zope.publisher.browser import BrowserView

class BundleView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.sitepath = zapi.getPath(zapi.getParent(self.context))
        self.configurations = self.findConfigurations(self.context, "")
        self.configurations.sort(self.compareConfigurations)
        self.services = self.findServices()

    # Methods called from the page template (bundle.pt)

    def update(self):
        if "allclear" in self.request:
            count = 0
            for path, obj in self.configurations:
                if obj.status != Unregistered:
                    obj.status = Unregistered
                    count += 1
            if count:
                get_transaction().note("deactivate bundle")
            return "unregistered %d configurations" % count
        activated = []
        registered = []
        for key, value in self.request.form.items():
            if value not in (Active, Registered):
                continue
            for path, obj in self.configurations:
                if key == path:
                    break
            else:
                raise ComponentLookupError(key)
        for path, obj in self.configurations:
            value = self.request.form.get(path)
            if value not in (Active, Registered):
                continue
            if obj.status != value:
                if value == Active:
                    activated.append(path)
                    obj.status = Active
                else:
                    registered.append(path)
                    obj.status = Registered
        s = ""
        if activated:
            s += "Activated: %s.\n" % (", ".join(activated))
        if registered:
            s += "Registered: %s.\n" % (", ".join(registered))
        if s:
            get_transaction().note("activate bundle")
        return s

    def listServices(self):
        infos = []
        for name in self.services:
            path, insite, inbundle = self.getServiceStatus(name)
            d = {"service": name,
                 "path": path,
                 "insite": insite,
                 "inbundle": inbundle}
            infos.append(d)
        return infos

    def listConfigurations(self):
        infos = []
        for path, obj in self.configurations:
            name, advice, conflict = self.getAdvice(obj)
            d = {"path": path,
                 "service": name,
                 "advice": advice,
                 "conflict": conflict,
                 "status": obj.status,
                 "usage": obj.usageSummary(),
                 "implementation": obj.implementationSummary()}
            infos.append(d)
        return infos

    # The rest are helper methods

    def getServiceStatus(self, name):
        try:
            svc = zapi.getService(self.context, name)
        except:
            svc = None
        path = ""
        insite = False
        if svc:
            try:
                path = zapi.getPath(svc)
            except:
                pass
            else:
                insite = (path == self.sitepath or
                          path.startswith(self.sitepath + "/"))
        inbundle = self.findServiceConfiguration(name)
        return path, insite, inbundle

    def getAdvice(self, obj):
        name = self.getServiceName(obj)
        conflict = ""
        sm = zapi.getServiceManager(obj)
        service = sm.queryLocalService(name)
        if not service:
            advice = Active
        else:
            registry = service.queryConfigurationsFor(obj)
            if not registry:
                advice = Active
            else:
                active = registry.active()
                if not active or active == obj:
                    advice = Active
                else:
                    advice = Registered
                    conflict = zapi.getPath(active)
        return name, advice, conflict

    def findServiceConfiguration(self, name):
        for path, obj in self.configurations:
            if IServiceConfiguration.isImplementedBy(obj):
                if obj.name == name:
                    return path
        return None

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
        t1 = (self.getAdjustedServiceName(obj1),
              obj1.usageSummary(),
              obj1.implementationSummary())
        t2 = (self.getAdjustedServiceName(obj2),
              obj2.usageSummary(),
              obj2.implementationSummary())
        return cmp(t1, t2)

    def findServices(self):
        sd = {}
        for path, obj in self.configurations:
            sd[self.getServiceName(obj)] = 1
        services = sd.keys()
        services.sort(self.compareServiceNames)
        return services

    def compareServiceNames(self, n1, n2):
        return cmp(self.adjustServiceName(n1), self.adjustServiceName(n2))

    def getAdjustedServiceName(self, configuration):
        name = self.getServiceName(configuration)
        return self.adjustServiceName(name)

    def adjustServiceName(self, name):
        # XXX Strange...  There's no symbol for it in servicenames.py
        if name == "Services":
            return ""
        else:
            return name

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
