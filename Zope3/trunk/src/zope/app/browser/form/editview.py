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
"""Edit View Classes

$Id: editview.py,v 1.38 2003/09/21 17:30:35 jim Exp $
"""
from datetime import datetime

from zope.schema import getFieldNamesInOrder
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.publisher.browser import BrowserView
from zope.security.checker import defineChecker, NamesChecker
from zope.component.view import provideView
from zope.component import getAdapter

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.form import WidgetsError
from zope.app.form.utility import setUpEditWidgets, applyWidgetsChanges
from zope.app.browser.form.submit import Update
from zope.app.event import publish
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass

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
        adapted = getAdapter(self.context, self.schema)
        if adapted is not self.context:
            adapted.__parent__ = self.context
        self.adapted = adapted
        setUpEditWidgets(self, self.schema, names=self.fieldNames,
                         content=self.adapted)

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
                changed = applyWidgetsChanges(self, content, self.schema,
                    names=self.fieldNames, exclude_readonly=True)
                # We should not generate events whan an adapter is used.
                # That's the adapter's job.
                if changed and self.context is self.adapted:
                    publish(content, ObjectModifiedEvent(content))
            except WidgetsError, errors:
                self.errors = errors
                status = _("An error occured.")
            else:
                setUpEditWidgets(self, self.schema, force=1,
                                 names=self.fieldNames, content=self.adapted)
                if changed:
                    formatter = self.request.locale.getDateTimeFormatter(
                        'medium')
                    status = _("Updated on ${date_time}")
                    status.mapping = {'date_time': formatter.format(
                        datetime.utcnow())}

        self.update_status = status
        return status


def EditViewFactory(name, schema, label, permission, layer,
                    template, default_template, bases, for_, fields,
                    fulledit_path=None, fulledit_label=None, menu=u'',
                    usage=u''):
    # XXX What about the __implements__ of the bases?
    class_ = SimpleViewClass(template, used_for=schema, bases=bases)
    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields

    class_.fulledit_path = fulledit_path
    if fulledit_path and (fulledit_label is None):
        fulledit_label = "Full edit"

    class_.fulledit_label = fulledit_label

    class_.generated_form = ViewPageTemplateFile(default_template)

    class_.usage = usage or (
        menu and globalBrowserMenuService.getMenuUsage(menu))

    defineChecker(class_,
                  NamesChecker(("__call__", "__getitem__",
                                "browserDefault", "publishTraverse"),
                               permission))

    provideView(for_, name, IBrowserPresentation, class_, layer)
