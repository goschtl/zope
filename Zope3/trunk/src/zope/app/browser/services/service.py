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
"""Adding components for components and configuration

$Id: service.py,v 1.3 2002/12/31 13:14:31 stevea Exp $
"""

from zope.app.browser.container.adding import Adding as ContentAdding
from zope.component import getView, getAdapter
from zope.proxy.context import ContextWrapper
from zope.app.interfaces.container import IZopeContainer
from zope.component import getServiceManager
from zope.publisher.browser import BrowserView
from zope.app.services.service import ServiceConfiguration
from zope.app.interfaces.services.configuration import IConfiguration
from zope.app.form.utility import setUpWidgets, getWidgetsDataForContent

__metaclass__ = type

class ComponentAdding(ContentAdding):
    """Adding component for components
    """

    menu_id = "add_component"

    def action(self, type_name, id):
        if not id:
            # Generate an id from the type name
            id = type_name
            if id in self.context:
                i=2
                while ("%s-%s" % (id, i)) in self.context:
                    i=i+1
                id = "%s-%s" % (id, i)
        return super(ComponentAdding, self).action(type_name, id)

class ConfigurationAdding(ContentAdding):
    """Adding component for configuration
    """

    menu_id = "add_configuration"

class EditConfiguration(BrowserView):
    """Adding component for service containers
    """

    menu_id = "add_component"

    def __init__(self, context, request):
        self.request = request
        self.context = context

    def action(self):
        """Perform actions depending on user input.


        """
        if 'add_submit' in self.request:
            self.request.response.redirect('+')
            return ''

        if 'keys' in self.request:
            k = self.request['keys']
        else:
            k = []

        msg = 'You must select at least one item to use this action'

        if 'remove_submit' in self.request:
            if not k: return msg
            self.remove_objects(k)
        elif 'top_submit' in self.request:
            if not k: return msg
            self.context.moveTop(k)
        elif 'bottom_submit' in self.request:
            if not k: return msg
            self.context.moveBottom(k)
        elif 'up_submit' in self.request:
            if not k: return msg
            self.context.moveUp(k)
        elif 'down_submit' in self.request:
            if not k: return msg
            self.context.moveDown(k)

        return ''

    def remove_objects(self, key_list):
        """Remove the directives from the container.
        """
        container = getAdapter(self.context, IZopeContainer)
        for item in key_list:
            del container[item]

    def configInfo(self):
        """Render View for each direcitves.
        """
        r = []
        for name, directive in self.context.items():
            d = ContextWrapper(directive, self.context, name = name)
            view = getView(d, 'ItemEdit', self.request)
            view.setPrefix('config'+str(name))
            r.append({'key': name, 'view': view})
        return r

class AddServiceConfiguration(BrowserView):

    def __init__(self, *args):
        super(AddServiceConfiguration, self).__init__(*args)
        setUpWidgets(self, IConfiguration)

    def services(self):
        service = getServiceManager(self.context.context)
        definitions = service.getServiceDefinitions()
        names = [name for (name, interface) in definitions]
        names.sort()
        return names

    def components(self):
        service_type = self.request['service_type']
        service = getServiceManager(self.context.context)
        type = service.getInterfaceFor(service_type)
        paths = [info['path']
                 for info in service.queryComponent(type=type)
                 ]
        paths.sort()
        return paths

    def action(self, service_type, component_path):
        sd = ServiceConfiguration(service_type, component_path)
        sd = self.context.add(sd)
        getWidgetsDataForContent(self, IConfiguration, sd)
        self.request.response.redirect(self.context.nextURL())
