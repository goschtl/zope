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
"""Views for local view configuration.

  ViewSeviceView -- it's a bit different from other services, as it
  has a lot of things in it, so we provide a search interface:

    search page
    browsing page

  PageConfigurationView -- calls validation on PageConfiguration.

$Id: view.py,v 1.10 2003/04/30 22:06:31 gvanrossum Exp $
"""
__metaclass__ = type

import md5

from zope.interface import Interface
from zope.schema import TextLine, BytesLine
from zope.component.interfaces import IPresentation
from zope.component import getAdapter, getServiceManager, getView
from zope.proxy.context import ContextWrapper
from zope.publisher.browser import BrowserView

from zope.app.browser.services.configuration import AddComponentConfiguration
from zope.app.component.interfacefield import InterfaceField
from zope.app.form.utility import setUpWidgets
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.interfaces.services.configuration import Unregistered, Registered
from zope.app.traversing import traverse, getPath, getParent, objectName

# XXX These are not used in this module, but are referenced in configure.zcml.
#  either configure.zcml should be fixed, or a comment should replace
#  this one to explain why configure.zcml is importing these two names
#  from here rather than from where they are defined.
from zope.app.services.view import ViewConfiguration, PageConfiguration

class IViewSearch(Interface):

    forInterface = InterfaceField(title=u"For interface",
                                  required=False,
                                  )
    presentationType = InterfaceField(title=u"Presentation interface",
                                      required=False,
                                      basetype=IPresentation
                                      )

    viewName = TextLine(title=u'View name',
                        required=False,
                        )

    layer = BytesLine(title=u'Layer',
                      required=False,
                      )


class ViewServiceView(BrowserView):

    """Helper class for the default view on the Views service."""

    def __init__(self, *args):
        super(ViewServiceView, self).__init__(*args)
        setUpWidgets(self, IViewSearch)

    def update(self):
        """Possibly deactivate or delete one or more page configurations.

        In that case, issue a message.
        """
        todo = self.request.get("selected")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not todo:
            if doDeactivate or doDelete:
                return "Please select at least one checkbox"
            return None
        if doDeactivate:
            return self._deactivate(todo)
        if doDelete:
            return self._delete(todo)

    def _getInfosFromKey(self, key):
        values = key.split(":")
        assert len(values) == 4, `values`
        viewName, forInterfaceName, presentationTypeName, layerName = values
        sm = getServiceManager(self.context)
        if forInterfaceName == "(Anything)":
            forInterface = None
        else:
            forInterface = sm.resolve(forInterfaceName)
        presentationType = sm.resolve(presentationTypeName)
        return self.context.getRegisteredMatching(forInterface,
                                                  presentationType,
                                                  viewName,
                                                  layerName)

    def _deactivate(self, todo):
        done = []
        for key in todo:
            infos = self._getInfosFromKey(key)
            for info in infos:
                (forInterface, presentationType,
                 registry, layer, viewName) = info
                registry = ContextWrapper(registry, self.context)
                obj = registry.active()
                if obj is not None:
                    obj.status = Registered
                    done.append(key)
        if done:
            return "Deactivated: " + ", ".join(done)
        else:
            return "None of the checked utilities were active"

    def _delete(self, todo):
        errors = []
        registries = []

        # Check that none of the registrations are active
        for key in todo:
            infos = self._getInfosFromKey(key)
            for info in infos:
                (forInterface, presentationType,
                 registry, layer, viewName) = info
                registry = ContextWrapper(registry, self.context)
                assert registry
                if registry.active() is not None:
                    errors.append(key)
                    continue
                registries.append(registry)
        if errors:
            return ("Can't delete active page%s: %s; "
                    "use the Deactivate button to deactivate" %
                    (len(errors) != 1 and "s" or "", ", ".join(errors)))

        # Now delete the registrations
        for registry in registries:
            assert registry
            assert registry.active() is None # Phase error
            for info in registry.info():
                conf = info['configuration']
                conf.status = Unregistered
                parent = getParent(conf)
                name = objectName(conf)
                container = getAdapter(parent, IZopeContainer)
                del container[name]

        return "Deleted: %s" % ", ".join([key for key in todo])

    def configInfo(self):
        """Do a search, or (by default) return all view pages."""
        input_for = self.forInterface.getData()
        input_type = self.presentationType.getData()
        input_name = self.viewName.getData()
        input_layer = self.layer.getData()

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
            view = getView(registry, "ChangeConfigurations", self.request)
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

class PageConfigurationView(BrowserView):

    """Helper class for the page edit form."""

    def update(self):
        super(PageConfigurationView, self).update()
        if "UPDATE_SUBMIT" in self.request:
            self.context.validate()
