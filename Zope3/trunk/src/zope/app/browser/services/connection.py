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
"""Connection registry support classes.

$Id: connection.py,v 1.13 2003/06/21 21:21:59 jim Exp $
"""

from zope.app.browser.services.registration import AddComponentRegistration
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.registration import IRegistered
from zope.component import getAdapter, getView
from zope.publisher.browser import BrowserView
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.traversing import traverse, getPath, getParent, getName

class Connections(BrowserView):

    # self.context is the local connection service

    def update(self):
        """Possibly deactivate or delete one or more connections.

        In that case, issue a message.
        """
        todo = self.request.get("selected")
        doActivate = self.request.get("Activate")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not todo:
            if doDeactivate or doDelete:
                return "Please select at least one checkbox"
            return None
        if doActivate:
            return self._activate(todo)
        if doDeactivate:
            return self._deactivate(todo)
        if doDelete:
            return self._delete(todo)

    def _activate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            obj = registry.active()
            if obj is None:
                # Activate the first registered registration
                obj = registry.info()[0]['registration']
                obj.status = ActiveStatus
                done.append(name)
        if done:
            return "Activated: " + ", ".join(done)
        else:
            return "All of the checked connections were already active"

    def _deactivate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            obj = registry.active()
            if obj is not None:
                obj.status = RegisteredStatus
                done.append(name)
        if done:
            return "Deactivated: " + ", ".join(done)
        else:
            return "None of the checked connections were active"

    def _delete(self, todo):
        errors = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            if registry.active() is not None:
                errors.append(name)
                continue
        if errors:
            return ("Can't delete active connection%s: %s; "
                    "use the Deactivate button to deactivate" %
                    (len(errors) != 1 and "s" or "", ", ".join(errors)))

        # 1) Delete the registrations
        connections = {}
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            assert registry.active() is None # Phase error
            for info in registry.info():
                conf = info['registration']
                obj = conf.getComponent()
                path = getPath(obj)
                connections[path] = obj
                conf.status = UnregisteredStatus
                parent = getParent(conf)
                name = getName(conf)
                container = getAdapter(parent, IZopeContainer)
                del container[name]

        # 2) Delete the connection objects
        for path, obj in connections.items():
            parent = getParent(obj)
            name = getName(obj)
            container = getAdapter(parent, IZopeContainer)
            del container[name]

        return "Deleted: %s" % ", ".join(todo)

    def getConfigs(self):
        L = []
        for name in self.context.listRegistrationNames():
            cr = self.context.queryRegistrations(name)
            active = cr.active()
            d = {"name": name,
                 "url": "",
                 "configurl": ("@@configureConnection.html?name=%s" % name),
                 }
            if active is not None:
                d["url"] = str(getView(active.getComponent(),
                                       "absolute_url",
                                       self.request))
            L.append((name, d))
        L.sort()
        return [d for name, d in L]

class ConfigureConnection(BrowserView):

    def update(self):
        cr = self.context.queryRegistrations(self.request['name'])
        form = getView(cr, "ChangeRegistrations", self.request)
        form.update()
        return form

class Registered(BrowserView):

    """View for displaying the registrations for a connection."""

    def uses(self):
        """Get a sequence of registration summaries."""
        component = self.context
        useconfig = getAdapter(component, IRegistered)
        result = []
        for path in useconfig.usages():
            config = traverse(component, path)
            url = getView(config, 'absolute_url', self.request)
            result.append({'name': config.name,
                           'path': path,
                           'url': url(),
                           'status': config.status,
                           })
        return result

class AddConnectionRegistration(AddComponentRegistration):

    pass
