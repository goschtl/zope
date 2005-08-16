##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Introspector View class

$Id$
"""
from zope.app.publisher.browser import BrowserView
from zope.app.introspector.interfaces import IIntrospector
from zope.app import zapi
from zope.component.exceptions import ComponentLookupError
from zope.interface import directlyProvides, directlyProvidedBy
from zope.proxy import removeAllProxies
from zope.app.component.interface import getInterface
from zope.app.servicenames import Services


class IntrospectorView(BrowserView):

    def getIntrospector(self):
        introspector = IIntrospector(self.context)
        introspector.setRequest(self.request)
        return introspector

    def getInterfaceURL(self, name):
        services = zapi.getService(Services, self.context)
        try:
            getInterface(self.context, name)
            url = zapi.getView(services, 'absolute_url', self.request)
        except ComponentLookupError:
            return ""
        return "%s/interfacedetail.html?id=%s" % (url, name)

    def update(self):
        if 'ADD' in self.request:
            for interface in self.getIntrospector().getMarkerInterfaceNames():
                if "add_%s" % interface in self.request:
                    interface = getInterface(self.context, interface)
                    ob = removeAllProxies(self.context)
                    directlyProvides(ob, directlyProvidedBy(ob), interface)

        if 'REMOVE' in self.request:
            for interface in self.getIntrospector().getDirectlyProvidedNames():
                if "rem_%s" % interface in self.request:
                    interface = getInterface(self.context, interface)
                    ob = removeAllProxies(self.context)
                    directlyProvides(ob, directlyProvidedBy(ob)-interface)

    def getServicesFor(self):
        services = []
        #sm = getServices()
        #for stype, interface in sm.getServiceDefinitions():
        #    try:
        #        service = getService(self.context, stype)
        #    except ComponentLookupError:
        #        pass
        #    else:
        #        # XXX IConfigureFor appears to have disappeared at some point
        #        adapter = IConfigureFor(service, None)
        #        if (adapter is not None
        #            and adapter.hasRegistrationFor(self.context)):
        #            search_result = service.getRegisteredMatching(
        #                self.context, None, [], self.context)
        #            directive_path = []
        #            if search_result:
        #                for eachitem in search_result:
        #                    dir_list = eachitem['directives']
        #                    component_path = eachitem['component_path']
        #                    for item in dir_list:
        #                        directives = item[2]
        #                        if directives:
        #                            if directives[0] is None:
        #                                directives = directives[1:]
        #                            for directive in directives:
        #                                for component in component_path:
        #                                    if component['component'] == directive:
        #                                        directive_path.append(component['path'])
        #            services.append({
        #                'type': stype,
        #                'service': service,
        #                'path': directive_path
        #                })
        return services
