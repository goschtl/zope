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
"""Gewneral registry-related views

$Id: __init__.py,v 1.14 2004/03/02 18:27:39 philikon Exp $
"""

from zope.app.browser.container.adding import Adding
from zope.app.browser.form.widget import RadioWidget, BrowserWidget
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.browser.interfaces.form import IBrowserWidget
from zope.app.interfaces.container import INameChooser

from zope.app.interfaces.services.registration import IRegistration
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.traversing import getName, traverse
from zope.component import getView, getServiceManager, getAdapter
from zope.proxy import removeAllProxies
from zope.app.publisher.browser import BrowserView
from zope.interface import implements


class NameRegistryView(BrowserView):

    indexMacros = index = ViewPageTemplateFile('nameregistry.pt')

    def update(self):

        names = list(self.context.listRegistrationNames())
        names.sort()

        items = []
        for name in names:
            registry = self.context.queryRegistrations(name)
            view = getView(registry, "ChangeRegistrations", self.request)
            view.setPrefix(name)
            view.update()
            cfg = registry.active()
            items.append(self._getItem(name, view, cfg))

        return items

    def _getItem(self, name, view, cfg):
        # hook for subclasses. returns a dict to append to an item
        return {"name": name,
                "active": cfg is not None,
                "inactive": cfg is None,
                "view": view,
                }


class NameComponentRegistryView(NameRegistryView):

    indexMacros = index = ViewPageTemplateFile('namecomponentregistry.pt')

    def _getItem(self, name, view, cfg):
        item_dict = NameRegistryView._getItem(self, name, view, cfg)
        if cfg is not None:
            ob = traverse(cfg, cfg.componentPath)
            url = str(getView(ob, 'absolute_url', self.request))
        else:
            url = None
        item_dict['url'] = url
        return item_dict


class RegistrationView(BrowserView):

    def __init__(self, context, request):
        super(RegistrationView, self).__init__(context, request)
        useconfig = getAdapter(self.context, IRegistered)
        self.registrations = useconfig.registrations()

    def update(self):
        """Make changes based on the form submission."""
        if len(self.registrations) > 1:
            self.request.response.redirect("registrations.html")
            return
        if "deactivate" in self.request:
            self.registrations[0].status = RegisteredStatus
        elif "activate" in self.request:
            if not self.registrations:
                # create a registration:
                self.request.response.redirect("addRegistration.html")
                return
            self.registrations[0].status = ActiveStatus

    def active(self):
        return self.registrations[0].status == ActiveStatus

    def registered(self):
        return bool(self.registrations)

    def registration(self):
        """Return the first registration.

        If there are no registrations, raises an error.
        """
        return self.registrations[0]


class NameRegistered:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def uses(self):
        component = self.context
        useconfig = getAdapter(component, IRegistered)
        result = []
        for path in useconfig.usages():
            config = traverse(component, path)
            description = None
            summaryMethod = getattr(config, "usageSummary", None)
            if summaryMethod:
                description = summaryMethod()
            url = getView(config, 'absolute_url', self.request)
            # XXX This assumes the registration implements
            #     INamedComponentRegistration rather than just
            #     IComponentRegistration.  ATM there are no
            #     counterexamples, so this is a sleeper bug;
            #     but what to do?  Could move the registration
            #     management up to INamedComponentRegistration,
            #     or could use path as default for name here.
            result.append({'name': config.name,
                           'path': path,
                           'url': url(),
                           'status': config.status,
                           'description': description or config.name,
                           })
        return result


class ChangeRegistrations(BrowserView):

    _prefix = 'registrations'
    name = _prefix + ".active"
    message = ''
    configBase = ''

    def setPrefix(self, prefix):
        self._prefix = prefix
        self.name = prefix + ".active"

    def applyUpdates(self):
        message = ''
        if 'submit_update' in self.request.form:
            id = self.request.form.get(self.name)
            if id == "disable":
                active = self.context.active()
                if active is not None:
                    self.context.activate(None)
                    message = _("Disabled")
            else:
                for info in self.context.info():
                    if info['id'] == id and not info['active']:
                        self.context.activate(info['registration'])
                        message = _("Updated")
                        break

        return message

    def update(self):

        message = self.applyUpdates()

        self.configBase = str(getView(getServiceManager(self.context),
                                      'absolute_url', self.request)
                              )

        registrations = self.context.info(True)

        # This is OK because registrations is just a list of dicts
        registrations = removeAllProxies(registrations)

        inactive = 1
        have_none = False
        for info in registrations:
            if info['active']:
                inactive = None
            else:
                info['active'] = None

            reg = info['registration']
            if reg is not None:
                info['summary'] = reg.implementationSummary()
            else:
                info['summary'] = ""
                info['id'] = 'disable'
                have_none = True

        if not have_none:
            # Add a dummy registration since the stack removes trailing None.
            registrations.append({"active": False,
                                  "id": "disable",
                                  "summary": ""})

        self.inactive = inactive
        self.registrations = registrations

        self.message = message


class RegistrationStatusWidget(RadioWidget):

    def _getDefault(self):
        return UnregisteredStatus

    def __call__(self):
        rendered_items = self.renderItems(self._showData())
        return "&nbsp;&nbsp;".join(rendered_items)


class ComponentPathWidget(BrowserWidget):
    """Widget for displaying component paths

    The widget doesn't actually allow editing. Rather it gets the
    value by inspecting its field's context. If the context is an
    IComponentRegistration, then it just gets its value from the
    component using the field's name. Otherwise, it uses the path to
    the context.
    """

    implements(IBrowserWidget)

    def __call__(self):
        """See zope.app.browser.interfaces.form.IBrowserWidget"""
        # Render as a link to the component
        field = self.context
        context = field.context
        if IRegistration.isImplementedBy(context):
            # It's a registration object. Just get the corresponding attr
            path = getattr(context, field.__name__)
            # The path may be relative; then interpret relative to ../..
            if not path.startswith("/"):
                context = traverse(context, "../..")
            component = traverse(context, path)
        else:
            # It must be a component that is about to be configured.
            component = context
            # Always use a relative path (just the component name)
            path = getName(context)

        url = getView(component, 'absolute_url', self.request)

        return ('<a href="%s/@@SelectedManagementView.html">%s</a>'
                % (url, path))

    def hidden(self):
        """See zope.app.browser.interfaces.form.IBrowserWidget"""
        return ''

    def hasInput(self):
        """See zope.app.interfaces.form.IWidget"""
        return 1

    def getInputValue(self):
        """See zope.app.interfaces.form.IWidget"""
        field = self.context
        context = field.context
        if IRegistration.isImplementedBy(context):
            # It's a registration object. Just get the corresponding attr
            path = getattr(context, field.getName())
        else:
            # It must be a component that is about to be configured.
            # Always return a relative path (just the component name)
            path = getName(context)

        return path


class AddComponentRegistration(BrowserView):
    """View for adding component registrations

    This class is used to define registration add forms.  It provides
    the ``add`` and ``nextURL`` methods needed when creating add forms
    for non-IAdding objects.  We need this here because registration
    add forms are views of the component being configured.
    """

    def add(self, registration):
        """Add a registration

        We are going to add the registration to the local
        registration manager. We don't want to hard code the name of
        this, so we'll simply scan the containing folder and add the
        registration to the first registration manager we find.

        """

        component = self.context

        # Get the registration manager for this folder
        folder = component.__parent__
        rm = folder.getRegistrationManager()

        name = getAdapter(rm, INameChooser).chooseName('', registration)
        rm[name] = registration
        return registration

    def nextURL(self):
        return "@@SelectedManagementView.html"


class RegistrationAdding(Adding):
    """Adding subclass for adding registrations."""

    menu_id = "add_registration"

    def nextURL(self):
        return str(getView(self.context, "absolute_url", self.request))


class EditRegistration(BrowserView):
    """A view on a registration manager, used by registrations.pt."""

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
        container = self.context
        for name in key_list:
            del container[name]

    def configInfo(self):
        """Render View for each directives."""
        result = []
        for name, configobj in self.context.items():
            url = str(getView(configobj, 'absolute_url', self.request))
            active = configobj.status == ActiveStatus
            summary1 = getattr(configobj, "usageSummary", None)
            summary2 = getattr(configobj, "implementationSummary", None)
            item = {'name': name, 'url': url, 'active': active}
            if summary1:
                item['line1'] = summary1()
            if summary2:
                item['line2'] = summary2()
            result.append(item)
        return result
