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

$Id: useconfiguration.py,v 1.2 2003/03/21 21:02:18 jim Exp $
"""

from zope.app.browser.component.interfacewidget import InterfaceWidget
from zope.app.browser.services.configuration import AddComponentConfiguration
from zope.app.form.widget import CustomWidget
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.traversing import traverse
from zope.component import getAdapter, getView
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
