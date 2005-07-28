##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Edit View Classes

$Id$
"""
from datetime import datetime
import transaction

from zope.schema import getFieldNamesInOrder
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.checker import defineChecker, NamesChecker

from zope.app import zapi
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.form.interfaces import WidgetsError
from zope.app.location.interfaces import ILocation
from zope.app.location import LocationProxy
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.publisher.browser import BrowserView
from zope.app.publisher.browser.globalbrowsermenuservice import \
    globalBrowserMenuService

from zope.app.form.utility import setUpEditWidgets, applyWidgetsChanges
from zope.app.form.browser.submit import Update


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
        super(EditView, self).__init__(context, request)
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

        if Update in self.request:
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
                transaction.abort()
            else:
                setUpEditWidgets(self, self.schema, source=self.adapted,
                                 ignoreStickyValues=True, 
                                 names=self.fieldNames)
                if changed:
                    self.changed()
                    formatter = self.request.locale.dates.getFormatter(
                        'dateTime', 'medium')
                    status = _("Updated on ${date_time}")
                    status.mapping = {'date_time': formatter.format(
                        datetime.utcnow())}

        self.update_status = status
        return status


def EditViewFactory(name, schema, label, permission, layer,
                    template, default_template, bases, for_, fields,
                    fulledit_path=None, fulledit_label=None, menu=u''):
    s = zapi.getGlobalService(zapi.servicenames.Presentation)
    class_ = SimpleViewClass(template, used_for=schema, bases=bases)
    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields

    class_.fulledit_path = fulledit_path
    if fulledit_path and (fulledit_label is None):
        fulledit_label = "Full edit"

    class_.fulledit_label = fulledit_label

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(("__call__", "__getitem__",
                                "browserDefault", "publishTraverse"),
                               permission))

    s.provideView(for_, name, IBrowserRequest, class_, layer)
