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
"""Helper classes for local view registry.

$Id: view.py,v 1.22 2003/08/07 17:41:03 srichter Exp $
"""
import md5


from zope.app.component.interfacefield import InterfaceField
from zope.app.context import ContextWrapper
from zope.app.form.utility import setUpWidgets
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.traversing import getPath, getParent, getName
from zope.component import getAdapter, getServiceManager, getView
from zope.component.interfaces import IPresentation
from zope.interface import Interface
from zope.schema import TextLine, BytesLine

__metaclass__ = type


class IViewSearch(Interface):

    forInterface = InterfaceField(
        title=u"For interface",
        required=False)

    presentationType = InterfaceField(
        title=u"Presentation interface",
        required=False,
        basetype=IPresentation)

    viewName = TextLine(
        title=u'View name',
        required=False)

    layer = BytesLine(
        title=u'Layer',
        required=False)


class _SharedBase:

    def _getRegistryFromKey(self, key):
        values = key.split(":")
        assert len(values) == 4, `values`
        viewName, forInterfaceName, presentationTypeName, layerName = values
        sm = getServiceManager(self.context)
        if forInterfaceName == "(Anything)":
            forInterface = None
        else:
            forInterface = sm.resolve(forInterfaceName)
        presentationType = sm.resolve(presentationTypeName)
        infos = self.context.getRegisteredMatching(forInterface,
                                                   presentationType,
                                                   viewName,
                                                   layerName)
        # We only want exact matches on 'forInterface'
        infos = [info for info in infos if info[0] == forInterface]
        assert len(infos) == 1
        registry = infos[0][2]
        registry = ContextWrapper(registry, self.context)
        assert registry
        return registry

    def _getSummaryFromRegistry(self, registry):
        assert registry
        # Return the summary of the first registration in the registry
        for info in registry.info():
            return info['registration'].usageSummary()
        assert 0


class ViewServiceView(_SharedBase):

    """Helper class for the default view on the Views service."""

    def __init__(self, *args):
        super(ViewServiceView, self).__init__(*args)
        setUpWidgets(self, IViewSearch)

    def update(self):
        """Possibly deactivate or delete one or more page registrations.

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
        for key in todo:
            registry = self._getRegistryFromKey(key)
            obj = registry.active()
            if obj is None:
                # Activate the first registered registration
                obj = registry.info()[0]['registration']
                obj.status = ActiveStatus
                done.append(self._getSummaryFromRegistry(registry))
        if done:
            s = _("Activated: ${activated_views}")
            s.mapping = {'activated_views': ", ".join(done)}
            return s
        else:
            return _("All of the checked views were already active")

    def _deactivate(self, todo):
        done = []
        for key in todo:
            registry = self._getRegistryFromKey(key)
            obj = registry.active()
            if obj is not None:
                obj.status = RegisteredStatus
                done.append(self._getSummaryFromRegistry(registry))
        if done:
            s = _("Deactivated: ${deactivated_views}")
            s.mapping = {'deactivated_views': ", ".join(done)}
            return s
        else:
            return _("None of the checked views were active")

    def _delete(self, todo):
        errors = []
        registries = []

        # Check that none of the registrations are active
        for key in todo:
            registry = self._getRegistryFromKey(key)
            if registry.active() is not None:
                errors.append(self._getSummaryFromRegistry(key))
                continue
            registries.append(registry)
        if errors:
            s = _("Can't delete active view(s): ${view_names}; "
                  "use the Deactivate button to deactivate")
            s.mapping = {'view_names': ", ".join(errors)}
            return s

        # Now delete the registrations
        done = []
        for registry in registries:
            assert registry
            assert registry.active() is None # Phase error
            done.append(self._getSummaryFromRegistry(registry))
            for info in registry.info():
                conf = info['registration']
                conf.status = UnregisteredStatus
                parent = getParent(conf)
                name = getName(conf)
                container = getAdapter(parent, IZopeContainer)
                del container[name]

        s = _("Deleted: ${cache_names}")
        s.mapping = {'cache_names': ", ".join(todo)}
        return s

    def configInfo(self):
        """Do a search, or (by default) return all view pages."""
        input_for = self.forInterface_widget.getData()
        input_type = self.presentationType_widget.getData()
        input_name = self.viewName_widget.getData()
        input_layer = self.layer_widget.getData()

        result = []
        for info in self.context.getRegisteredMatching(
            input_for, input_type, input_name, input_layer):

            forInterface, presentationType, registry, layer, viewName = info

            if not registry:
                continue

            if forInterface is None:
                forInterface = "(Anything)"
            else:
                forInterface = (
                    forInterface.__module__ +"."+ forInterface.__name__)

            shortType = presentationType.__name__
            presentationType = (
                presentationType.__module__ +"."+ presentationType.__name__)

            registry = ContextWrapper(registry, self.context)
            view = getView(registry, "ChangeRegistrations", self.request)
            # XXX Why are we setting this unique prefix?
            prefix = md5.new('%s %s' %
                             (forInterface, presentationType)).hexdigest()
            view.setPrefix(prefix)
            view.update()

            if input_name is not None:
                viewName = None

            if input_layer is not None:
                layer = None

            key = "%s:%s:%s:%s" % (viewName, forInterface,
                                   presentationType, layer)

            rec = {'forInterface': forInterface,
                   'presentationType': presentationType,
                   'shortType': shortType,
                   'summary': self._getSummaryFromRegistry(registry),
                   'view': view,
                   'viewName': viewName,
                   'layer': layer,
                   'key': key,
                   'configurl': "@@configureView.html?key=%s" % key,
                   'url': "",
                 }

            active = registry.active()
            if active is not None:
                rec['url'] = getPath(active)

            result.append(rec)

        return result

class PageRegistrationView:
    """Helper class for the page edit form."""

    def update(self):
        super(PageRegistrationView, self).update()
        if "UPDATE_SUBMIT" in self.request:
            self.context.validate()

class ConfigureView(_SharedBase):

    def update(self):
        key = self.request['key']
        registry = self._getRegistryFromKey(key)
        form = getView(registry, "ChangeRegistrations", self.request)
        form.update()
        return form

    def summary(self):
        key = self.request['key']
        registry = self._getRegistryFromKey(key)
        return self._getSummaryFromRegistry(registry)
