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
"""Cache registry support classes.

$Id: cache.py,v 1.12 2003/08/07 17:41:03 srichter Exp $
"""
from zope.app.browser.services.registration import AddComponentRegistration
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.traversing import traverse, getPath, getParent, getName
from zope.component import getAdapter, getView

class Caches:
    # self.context is the local caching service

    def update(self):
        """Possibly delete one or more caches.

        In that case, issue a message.
        """
        todo = self.request.get("selected")
        doActivate = self.request.get("Activate")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not todo:
            if doActivate or doDeactivate or doDelete:
                return _("Please select at least one checkbox")
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
            s = _("Activated: ${activated_caches}")
            s.mapping = {'activated_caches': ", ".join(done)}
            return s
        else:
            return _("All of the checked caches were already active")

    def _deactivate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            obj = registry.active()
            if obj is not None:
                obj.status = RegisteredStatus
                done.append(name)
        if done:
            s = _("Deactivated: ${deactivated_caches}")
            s.mapping = {'deactivated_caches': ", ".join(done)}
            return s
        else:
            return _("None of the checked caches were active")

    def _delete(self, todo):
        errors = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            if registry.active() is not None:
                errors.append(name)
                continue
        if errors:
            s = _("Can't delete active cache(s): ${cache_names}; "
                  "use the Deactivate button to deactivate")
            s.mapping = {'cache_names': ", ".join(errors)}
            return s

        # 1) Delete the registrations
        caches = {}
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            assert registry.active() is None # Phase error
            for info in registry.info():
                conf = info['registration']
                obj = conf.getComponent()
                path = getPath(obj)
                caches[path] = obj
                conf.status = UnregisteredStatus
                parent = getParent(conf)
                name = getName(conf)
                container = getAdapter(parent, IZopeContainer)
                del container[name]

        # 2) Delete the cache objects
        for path, obj in caches.items():
            parent = getParent(obj)
            name = getName(obj)
            container = getAdapter(parent, IZopeContainer)
            del container[name]

        s = _("Deleted: ${cache_names}")
        s.mapping = {'cache_names': ", ".join(todo)}
        return s

    def getConfigs(self):
        L = []
        for name in self.context.listRegistrationNames():
            cr = self.context.queryRegistrations(name)
            active = cr.active()
            d = {"name": name,
                 "url": "",
                 "configurl": ("@@configureCache.html?name=%s" % name),
                 }
            if active is not None:
                d["url"] = str(getView(active.getComponent(),
                                       "absolute_url",
                                       self.request))
            L.append((name, d))
        L.sort()
        return [d for name, d in L]

class ConfigureCache:

    def update(self):
        cr = self.context.queryRegistrations(self.request['name'])
        form = getView(cr, "ChangeRegistrations", self.request)
        form.update()
        return form

class Registered:
    """View for displaying the registrations for a cache."""

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

class AddCacheRegistration(AddComponentRegistration):
    pass
