##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Provide basic browser functionality

$Id$
"""

import Acquisition
from  Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from interfaces import ITraversable
from datetime import datetime
from zope.interface import implements
from zope.interface.common.mapping import IItemMapping
from zope.component import getView
from zope.component import getViewProviding
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from zope.app.location.interfaces import ILocation
from zope.app.location import LocationProxy
from zope.app.form.utility import setUpEditWidgets, applyWidgetsChanges
from zope.app.form.browser.submit import Update
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class BrowserView(Acquisition.Explicit):
    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # XXX do not create any methods on the subclass called index_html,
    # as this makes Zope 2 traverse into that first!

InitializeClass(BrowserView)

class AbsoluteURL(BrowserView):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    (original: zope.app.traversing.browser.absoluteurl)
    """

    def __init__(self, context, request):
        self.context, self.request = context, request

    implements(IAbsoluteURL)

    def __str__(self):
        context = aq_inner(self.context)
        return context.absolute_url()

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        request = self.request

        container = aq_parent(aq_inner(context))
        if container is None or not ITraversable.providedBy(container):
            return ({'name': context.getId(),
                     'url': context.absolute_url()
                     },)

        view = getViewProviding(container, IAbsoluteURL, request)
        base = tuple(view.breadcrumbs())
        name = context.getId()
        base += ({'name': name,
                  'url': ("%s/%s" % (base[-1]['url'], name))
                  },)

        return base


class SiteAbsoluteURL(AbsoluteURL):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    This one is just used to stop breadcrumbs from crumbing up
    to the Zope root.

    (original: zope.app.traversing.browser.absoluteurl)
    """

    def breadcrumbs(self):
        context = self.context
        request = self.request

        return ({'name': context.getId(),
                 'url': context.absolute_url()
                 },)


class EditView(BrowserView):
    """Simple edit-view base class

    Subclasses should provide a schema attribute defining the schema
    to be edited.
    """

    errors = ()
    update_status = None
    label = ''

    # Fall-back field names computes from schema
    fieldNames = property(lambda self: getFieldNamesInOrder(self.schema))
    # Fall-back template
    generated_form = ViewPageTemplateFile('edit.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self._setUpWidgets()

    def _setUpWidgets(self):
        adapted = self.schema(self.context)
        if adapted is not self.context:
            if not ILocation.providedBy(adapted):
                adapted = LocationProxy(adapted)
            adapted.__parent__ = self.context
        self.adapted = adapted
        setUpEditWidgets(self, self.schema, source=self.adapted,
                         names=self.fieldNames)

    def setPrefix(self, prefix):
        for widget in self.widgets():
            widget.setPrefix(prefix)

    def widgets(self):
        return [getattr(self, name+'_widget')
                for name in self.fieldNames]

    def changed(self):
        # This method is overridden to execute logic *after* changes
        # have been made.
        pass

    def update(self):
        if self.update_status is not None:
            # We've been called before. Just return the status we previously
            # computed.
            return self.update_status

        status = ''

        content = self.adapted

        if Update in self.request.form.keys():
            changed = False
            try:
                changed = applyWidgetsChanges(self, self.schema,
                    target=content, names=self.fieldNames)
                # We should not generate events when an adapter is used.
                # That's the adapter's job.
                if changed and self.context is self.adapted:
                    notify(ObjectModifiedEvent(content))
            except WidgetsError, errors:
                self.errors = errors
                status = _("An error occured.")
                get_transaction().abort()
            else:
                setUpEditWidgets(self, self.schema, source=self.adapted,
                                 ignoreStickyValues=True,
                                 names=self.fieldNames)
                if changed:
                    self.changed()
                    # XXX: Needs i18n support:
                    # formatter = self.request.locale.dates.getFormatter(
                    #     'dateTime', 'medium')
                    # status = _("Updated on ${date_time}")
                    # status.mapping = {'date_time': formatter.format(
                    #     datetime.utcnow())}
                    status = "Updated on %s" % str(datetime.utcnow())

        self.update_status = status
        return status


class Macros:

    implements(IItemMapping)

    macro_pages = ()
    aliases = {
        'view': 'page',
        'dialog': 'page',
        'addingdialog': 'page'
        }

    def __getitem__(self, key):
        key = self.aliases.get(key, key)
        context = self.context
        request = self.request
        for name in self.macro_pages:
            page = getView(context, name, request)
            try:
                v = page[key]
            except KeyError:
                pass
            else:
                return v
        raise KeyError, key

class StandardMacros(BrowserView, Macros): pass

