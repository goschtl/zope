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
from zope.publisher.browser import BrowserView
from zope.app.interfaces.introspector import IIntrospector
from zope.component import getAdapter
# XXX only used for commented-out section below
# from zope.component import getServiceManager, getServiceDefinitions, \
#      queryAdapter, getService
# from zope.component.exceptions import ComponentLookupError


class IntrospectorView(BrowserView):

    def getIntrospector(self):
        introspector = getAdapter(self.context, IIntrospector)
        introspector.setRequest(self.request)
        return introspector

    def getServicesFor(self):
        services = []
        #sm = getServiceManager(self.context)
        #for stype, interface in sm.getServiceDefinitions():
        #    try:
        #        service = getService(self.context, stype)
        #    except ComponentLookupError:
        #        pass
        #    else:
        #        # XXX IConfigureFor appears to have disappeared at some point
        #        adapter = queryAdapter(service, IConfigureFor)
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
