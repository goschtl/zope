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
"""Gewneral configuration-related views

$Id: __init__.py,v 1.5 2003/04/28 15:54:11 gvanrossum Exp $
"""

from zope.app.browser.container.adding import Adding
from zope.app.browser.form.widget import BrowserWidget
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.configuration import Active, Registered
from zope.app.interfaces.services.configuration import IComponentConfiguration
from zope.app.interfaces.services.configuration import Unregistered
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.traversing import getPath, traverse
from zope.component import getView, getServiceManager, getAdapter
from zope.proxy.context import getWrapperContainer, ContextWrapper
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView


class NameConfigurableView(BrowserView):

    indexMacros = index = ViewPageTemplateFile('nameconfigurable.pt')

    def update(self):

        names = list(self.context.listConfigurationNames())
        names.sort()

        items = []
        for name in names:
            registry = self.context.queryConfigurations(name)
            view = getView(registry, "ChangeConfigurations", self.request)
            view.setPrefix(name)
            view.update()
            cfg = registry.active()
            active = cfg is not None
            items.append(self._getItem(name, view, cfg))

        return items

    def _getItem(self, name, view, cfg):
        # hook for subclasses. returns a dict to append to an item
        return {"name": name,
                "active": cfg is not None,
                "inactive": cfg is None,
                "view": view,
                }


class NameComponentConfigurableView(NameConfigurableView):

    indexMacros = index = ViewPageTemplateFile('namecomponentconfigurable.pt')

    def _getItem(self, name, view, cfg):
        item_dict = NameConfigurableView._getItem(self, name, view, cfg)
        if cfg is not None:
            ob = traverse(cfg, cfg.componentPath)
            url = str(getView(ob, 'absolute_url', self.request))
        else:
            url = None
        item_dict['url'] = url
        return item_dict


class NameUseConfiguration:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def uses(self):
        component = self.context
        useconfig = getAdapter(component, IUseConfiguration)
        result = []
        for path in useconfig.usages():
            config = traverse(component, path)
            url = getView(config, 'absolute_url', self.request)
            # XXX This assumes the configuration implements
            #     INamedComponentConfiguration rather than just
            #     IComponentConfiguration.  ATM there are no
            #     counterexamples, so this is a sleeper bug;
            #     but what to do?  Could move the configuration
            #     management up to INamedComponentConfiguration,
            #     or could use path as default for name here.
            result.append({'name': config.name,
                           'path': path,
                           'url': url(),
                           'status': config.status,
                           })
        return result


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

            info['summary'] = info['configuration'].implementationSummary()

        self.inactive = inactive
        self.configurations = configurations

        self.message = message


class ConfigurationStatusWidget(BrowserWidget):

    def __call__(self):
        checked = self._showData() or Unregistered
        result = [
            ('<label>'
             '<input type="radio" name="%s" value="%s"%s>'
             '&nbsp;'
             '%s'
             '</label>'
             % (self.name, v, (v == checked and ' checked' or ''), v)
             )
            for v in (Unregistered, Registered, Active)
            ]
        return ' '.join(result)


class ComponentPathWidget(BrowserWidget):
    """Widget for displaying component paths

    The widget doesn't actually allow editing. Rather it gets the
    value by inspecting its field's context. If the context is an
    IComponentConfiguration, then it just gets it's value from the
    component using the field's name. Otherwise, it uses the path to
    the context.
    """

    __implements__ =  IBrowserWidget


    def __call__(self):
        "See zope.app.interfaces.browser.form.IBrowserWidget"
        # Render as a link to the component
        field = self.context
        context = field.context 
        if IComponentConfiguration.isImplementedBy(context):
            # It's a configuration object. Just get the corresponsing attr
            path = getattr(context, field.__name__)
            component = traverse(context, path)
        else:
            # It must be a component that is about to be configured.
            component = context
            path = getPath(context)

        url = getView(component, 'absolute_url', self.request)

        return ('<a href="%s/@@SelectedManagementView.html">%s</a>'
                % (url, path))

    def hidden(self):
        "See zope.app.interfaces.browser.form.IBrowserWidget"
        return ''

    def getData(self):
        "See zope.app.interfaces.form.IWidget"
        field = self.context
        context = field.context 
        if IComponentConfiguration.isImplementedBy(context):
            # It's a configuration object. Just get the corresponsing attr
            # XXX this code has no unittests !!!
            path = getattr(context, field.__name__)
        else:
            # It must be a component that is about to be configured.
            path = getPath(context)

        return path

    def haveData(self):
        "See zope.app.interfaces.form.IWidget"
        return True


class AddComponentConfiguration(BrowserView):
    """View for adding component configurations

    This class is used to define configuration add forms.  It provides
    tha ``add`` and ``nextURL`` methods needed when creating add forms
    for non IAdding object. We need this here because configuration
    add forms are views of the component being configured.
    """
    
    def add(self, configuration):
        """Add a configuration

        We are going to add the configuration to the local
        configuration manager. We don't want to hard code the name of
        this, so we'll simply scan the containing folder and add the
        configuration to the first configuration manager we find.

        """

        component = self.context
        
        # Get the configuration manager for this folder
        folder = getWrapperContainer(component)
        configure = folder.getConfigurationManager()

        # Adapt to IZopeContainer, which takes care of generating
        # standard events and calling standard hooks
        container = getAdapter(configure, IZopeContainer)

        # Now add the item, saving the key, which is picked by the config
        key = container.setObject("", configuration)

        # and return the config in context by fetching it from the container
        return container[key]

    def nextURL(self):
        return "@@SelectedManagementView.html"


class ConfigurationAdding(Adding):
    """Adding subclass for adding configurations."""

    menu_id = "add_configuration"

    def nextURL(self):
        return str(getView(self.context, "absolute_url", self.request))


class EditConfiguration(BrowserView):
    """A view on a configuration manager, used by configurations.pt."""

    def __init__(self, context, request):
        self.request = request
        self.context = context

    def update(self):
        """Perform actions depending on user input."""

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
        elif 'refresh_submit' in self.request:
            pass # Nothing to do

        return ''

    def remove_objects(self, key_list):
        """Remove the directives from the container."""
        container = getAdapter(self.context, IZopeContainer)
        for item in key_list:
            del container[item]

    def configInfo(self):
        """Render View for each directives."""
        result = []
        for name, configobj in self.context.items():
            configobj = ContextWrapper(configobj, self.context, name=name)
            url = str(getView(configobj, 'absolute_url', self.request))
            active = configobj.status == Active
            summary1 = getattr(configobj, "usageSummary", None)
            summary2 = getattr(configobj, "implementationSummary", None)
            item = {'name': name, 'url': url, 'active': active}
            if summary1:
                item['line1'] = summary1()
            if summary2:
                item['line2'] = summary2()
            result.append(item)
        return result
