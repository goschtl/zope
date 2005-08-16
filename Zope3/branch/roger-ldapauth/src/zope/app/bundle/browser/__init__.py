##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
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
registrations in the bundle are activated, unless they conflict with
existing registrations.  This is an interactive process.

XXX This interim code is much less ambitious: it just provides a view
on a (site-management) folder that displays all registrations in a
bundle and lets the user activate them.

$Id$
"""
import re
from transaction import get_transaction

from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.container.interfaces import IReadContainer
from zope.app.registration.interfaces import \
     IRegistration, RegisteredStatus, ActiveStatus, UnregisteredStatus
from zope.app.site.interfaces import IServiceRegistration
from zope.component import ComponentLookupError
from zope.app.publisher.browser import BrowserView

class BundleView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.mypath = zapi.getPath(self.context)
        self.myversion = self.parseVersion(self.mypath)
        # Compute sitepath as the parent of mypath
        sitepath = zapi.getPath(self.context)
        i = sitepath.rfind("/")
        if i > 0:
            sitepath = sitepath[:i]
        elif i == 0:
            sitepath = "/"
        else:
            sitepath = ""
        self.sitepath = sitepath
        self.registrations = self.findRegistrations(self.context, "")
        self.registrations.sort(self.compareRegistrations)
        self.services = self.findServices()

    # Methods called from the page template (bundle.pt)

    def update(self):
        if not self.request.form:
            return
        if zapi.getName(self.context) == "default":
            # XXX This is not right: we should be able to tell bundles
            # from non-bundles and only allow this command for
            # bundles.  The Bundle tab should only be present for
            # bundles.  But for now, we simply prevent the user from
            # making a big mistake and changing the default folder.
            return "ERROR: Won't change the default folder"
        if "allclear" in self.request:
            count = 0
            for path, obj in self.registrations:
                if obj.status != UnregisteredStatus:
                    obj.status = UnregisteredStatus
                    count += 1
            if count:
                get_transaction().note("deactivate bundle")
            status = _("unregistered ${count} registrations")
            status.mapping = {'count': str(count)}
            return status
        activated = []
        registered = []
        for key, value in self.request.form.items():
            if value not in (ActiveStatus, RegisteredStatus):
                continue
            for path, obj in self.registrations:
                if key == path:
                    break
            else:
                raise ComponentLookupError(key)
        for path, obj in self.registrations:
            value = self.request.form.get(path)
            if value not in (ActiveStatus, RegisteredStatus):
                continue
            if obj.status != value:
                if value == ActiveStatus:
                    activated.append(path)
                    obj.status = ActiveStatus
                else:
                    registered.append(path)
                    obj.status = RegisteredStatus
        s = ""
        mapping = {}
        if activated:
            s += _("Activated: ${activated}.\n")
            mapping['activated'] = ", ".join(activated)
        if registered:
            s += _("Registered: ${registered}.\n")
            mapping['registered'] = ", ".join(registered)
        if s:
            get_transaction().note("activate bundle")
        # We have to do that again, since the adding to a message id makes it
        # a unicode string again.
        s = _(s)
        s.mapping = mapping
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

    def listRegistrations(self):
        infos = []
        for path, obj in self.registrations:
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
            svc = zapi.getService(name)
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
        inbundle = self.findServiceRegistration(name)
        return path, insite, inbundle

    def getAdvice(self, obj):
        name = self.getServiceName(obj)
        advice = ActiveStatus
        conflict = ""
        sm = zapi.getServices(obj)
        service = sm.queryLocalService(name)
        if service:
            registry = service.queryRegistrationsFor(obj)
            if registry:
                active = registry.active()
                if active and active != obj:
                    conflict = zapi.getPath(active)
                    if not self.inOlderVersion(active):
                        advice = RegisteredStatus
        return name, advice, conflict

    def inOlderVersion(self, obj):
        # Return whether obj (an active component) belongs to an older
        # version of the same bundle we're proposing to activate here.
        # XXX This assumes sites are named with ++etc++site; there is
        # no support for the older ++etc++Services.
        path = zapi.getPath(obj)
        prefix = "/++etc++site/"
        i = path.rfind(prefix) # (can the prefix occur twice?)
        if i < 0:
            return False
        i += len(prefix) # points just after the second "/"
        i = path.find("/", i) # finds next slash after that
        if i >= 0:
            path = path[:i]
        # Now path is of the form ".../++etc++site/name-version"
        version = self.parseVersion(path)
        if not version:
            return False
        i = path.rfind("-") + 1
        return self.mypath[:i] == path[:i] and self.myversion > version

    nineDigits = re.compile(r"^\d{1,9}$")

    def parseVersion(self, path):
        # Return a list containing the version numbers, suitably
        # modified for sane version comparison.  If there is no
        # version number, return None.  A version number is any number
        # of dot-separated integers of at most 9 digits, optionally
        # followed by another dot and something like "a1" or "b1"
        # indicating an alpha or beta version.  If no alpha or beta
        # version is present, "f" is assumed (indicating "final").
        # ("f" is chosen to compare higher than "a1", "b1" or "c1" but
        # lower than "p1"; "p1" is sometimes used to indicate a patch
        # release.)  Examples:
        #
        # "/foo/bar-boo"        -> None
        # "/foo/bar-boo-1.0"    -> ["f000000001", "f000000000", "f"]
        # "/foo/bar-boo-1.0.f"  -> ["f000000001", "f000000000", "f"]
        # "/foo/bar-boo-1.0.a1" -> ["f000000001", "f000000000", "a1"]
        #
        # Note that we do a string compare on the alpha/beta version
        # number; "a10" will compare less than "a2".  OTOH, the
        # integers are padded with leading zeros, so "10" will compare
        # higher than "2".
        i = path.rfind("/") + 1
        base = path[i:]
        i = base.rfind("-") + 1
        if not i:
            return None # No version
        version = base[i:]
        parts = version.split(".")
        last = parts[-1]
        if self.nineDigits.match(last):
            last = "f"
        else:
            last = last.lower()
            del parts[-1]
            if not parts:
                return None
        for i in range(len(parts)):
            p = parts[i]
            if not self.nineDigits.match(p):
                return None
            parts[i] = "f" + "0"*(9-len(p)) + p
        parts.append(last)
        return parts

    def findServiceRegistration(self, name):
        for path, obj in self.registrations:
            if IServiceRegistration.providedBy(obj):
                if obj.name == name:
                    return path
        return None

    def findRegistrations(self, f, prefix):
        alist = []
        for name, obj in f.items():
            if IRegistration.providedBy(obj):
                alist.append((prefix+name, obj))
            elif IReadContainer.providedBy(obj):
                alist.extend(self.findRegistrations(obj, prefix+name+"/"))
        return alist

    def compareRegistrations(self, c1, c2):
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
        for path, obj in self.registrations:
            sd[self.getServiceName(obj)] = 1
        services = sd.keys()
        services.sort(self.compareServiceNames)
        return services

    def compareServiceNames(self, n1, n2):
        return cmp(self.adjustServiceName(n1), self.adjustServiceName(n2))

    def getAdjustedServiceName(self, registration):
        name = self.getServiceName(registration)
        return self.adjustServiceName(name)

    def adjustServiceName(self, name):
        # XXX Strange...  There's no symbol for it in servicenames.py
        if name == "Services":
            return ""
        else:
            return name

    def getServiceName(self, registration):
        # Return the service associated with a registration.
        return registration.serviceType
