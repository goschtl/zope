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
"""Use-Configuration view for utilities.

$Id: useconfiguration.py,v 1.3 2003/04/03 22:05:32 fdrake Exp $
"""

from zope.app.browser.component.interfacewidget import InterfaceWidget
from zope.app.browser.services.configuration import AddComponentConfiguration
from zope.app.form.widget import CustomWidget
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.traversing import traverse
from zope.component import getAdapter, getServiceManager, getView
from zope.interface.implements import flattenInterfaces
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView

class UseConfiguration(BrowserView):
    """View for displaying the configurations for a utility.
    """

    def uses(self):
        """Get a sequence of configuration summaries
        """
        component = self.context
        useconfig = getAdapter(component, IUseConfiguration)
        result = []
        for path in useconfig.usages():
            config = traverse(component, path)
            url = getView(config, 'absolute_url', self.request)
            result.append({'name': config.name,
                           'interface': config.interface.__name__,
                           'path': path,
                           'url': url(),
                           'status': config.status,
                           })
        return result
        

class UtilityInterfaceWidget(InterfaceWidget):
    """Custom widget to select an interface from the component's interfaces.
    """

    def __call__(self):
        field = self.context
        component = field.context
        # XXX Have to remove proxies because flattenInterfaces
        #     doesn't work with proxies.
        bare = removeAllProxies(component)
        # Compute the list of interfaces that the component implements
        interfaces = [
            interface
            for interface in flattenInterfaces(bare.__implements__)
            if list(interface) # Does the interface define any names
            ]
        result = ['\n<select name="%s">' % self.name]
        for interface in interfaces:
            result.append('  <option value="%s.%s">%s</option>' %
                          (interface.__module__, interface.__name__,
                           interface.__name__))
        result.append('</select>')
        return '\n'.join(result)
        

class AddConfiguration(AddComponentConfiguration):
    """View for adding a utility configuration.


    We could just use AddComponentConfiguration, except that we need a
    custom interface widget.

    This is a view on a local utility, configured by an <addform>
    directive.
    """

    interface = CustomWidget(UtilityInterfaceWidget)


class Utilities(BrowserView):
    def getConfigs(self):
        L = []
        for iface, name, cr in self.context.getRegisteredMatching():
            active = cr.active()
            ifname = _interface_name(iface)
            d = {"interface": ifname,
                 "name": name,
                 "url": "",
                 "configurl": ("@@configureutility.html?interface=%s&name=%s"
                               % (ifname, name)),
                 }
            if active is not None:
                d["url"] = str(getView(active.getComponent(),
                                       "absolute_url",
                                       self.request))
            L.append((ifname, name, d))
        L.sort()
        return [d for ifname, name, d in L]


class ConfigureUtility(BrowserView):
    def update(self):
        sm = getServiceManager(self.context)
        iface = sm.resolve(self.request['interface'])
        name = self.request['name']
        cr = self.context.queryConfigurations(name, iface)
        form = getView(cr, "ChangeConfigurations", self.request)
        form.update()
        return form


def _interface_name(iface):
    return "%s.%s" % (iface.__module__, iface.__name__)
