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
"""Cache configuration support classes.

$Id: cache.py,v 1.10 2003/06/13 17:41:13 stevea Exp $
"""

from zope.app.browser.services.configuration import AddComponentConfiguration
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.component import getAdapter, getView
from zope.publisher.browser import BrowserView
from zope.app.interfaces.services.configuration \
     import Unregistered, Registered, Active
from zope.app.traversing import traverse, getPath, getParent, getName

class Caches(BrowserView):

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
            registry = self.context.queryConfigurations(name)
            obj = registry.active()
            if obj is None:
                # Activate the first registered configuration
                obj = registry.info()[0]['configuration']
                obj.status = Active
                done.append(name)
        if done:
            return "Activated: " + ", ".join(done)
        else:
            return "All of the checked caches were already active"

    def _deactivate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryConfigurations(name)
            obj = registry.active()
            if obj is not None:
                obj.status = Registered
                done.append(name)
        if done:
            return "Deactivated: " + ", ".join(done)
        else:
            return "None of the checked caches were active"

    def _delete(self, todo):
        errors = []
        for name in todo:
            registry = self.context.queryConfigurations(name)
            assert registry
            if registry.active() is not None:
                errors.append(name)
                continue
        if errors:
            return ("Can't delete active cache%s: %s; "
                    "use the Deactivate button to deactivate" %
                    (len(errors) != 1 and "s" or "", ", ".join(errors)))

        # 1) Delete the registrations
        caches = {}
        for name in todo:
            registry = self.context.queryConfigurations(name)
            assert registry
            assert registry.active() is None # Phase error
            for info in registry.info():
                conf = info['configuration']
                obj = conf.getComponent()
                path = getPath(obj)
                caches[path] = obj
                conf.status = Unregistered
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

        return "Deleted: %s" % ", ".join(todo)

    def getConfigs(self):
        L = []
        for name in self.context.listConfigurationNames():
            cr = self.context.queryConfigurations(name)
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

class ConfigureCache(BrowserView):

    def update(self):
        cr = self.context.queryConfigurations(self.request['name'])
        form = getView(cr, "ChangeConfigurations", self.request)
        form.update()
        return form

class UseConfiguration(BrowserView):

    """View for displaying the configurations for a cache."""

    def uses(self):
        """Get a sequence of configuration summaries."""
        component = self.context
        useconfig = getAdapter(component, IUseConfiguration)
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

class AddCacheConfiguration(AddComponentConfiguration):

    pass
