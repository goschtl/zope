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

$Id: changeconfigurations.py,v 1.3 2003/03/18 21:02:20 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.component import getView, getServiceManager
from zope.proxy.introspection import removeAllProxies

class ChangeConfigurations(BrowserView):

    _prefix = 'configurations'
    name = _prefix + ".active"
    message = ''
    configBase = ''

    def setPrefix(self, prefix):
        self._prefix = prefix
        self.name = prefix + ".active"

    def applyUpdates(self):
        message = ''
        if 'submit_update' in self.request.form:
            active = self.request.form.get(self.name)
            if active == "disable":
                active = self.context.active()
                if active is not None:
                    self.context.deactivate(active)
                    message = "Disabled"
            else:
                for info in self.context.info():
                    if info['id'] == active:
                        if not info['active']:
                            self.context.activate(info['configuration'])
                            message = "Updated"

        return message

    def update(self):

        message = self.applyUpdates()

        self.configBase = str(getView(getServiceManager(self.context),
                                      'absolute_url', self.request)
                              )

        configurations = self.context.info()

        # This is OK because configurations is just a list of dicts
        configurations = removeAllProxies(configurations)

        inactive = 1
        for info in configurations:
            if info['active']:
                inactive = None
            else:
                info['active'] = None

            info['summary'] = getView(info['configuration'],
                                      'ConfigurationSummary',
                                      self.request)

        self.inactive = inactive
        self.configurations = configurations

        self.message = message
