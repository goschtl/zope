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
"""
$Id: editview.py,v 1.31 2003/08/02 09:11:08 anthony Exp $
"""

import os

from datetime import datetime
from zope.configuration.exceptions import ConfigurationError

from zope.schema.interfaces import ValidationError
from zope.schema import getFieldNamesInOrder

from zope.interface import classProvides, implements

from zope.configuration.action import Action
from zope.app.context import ContextWrapper
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.browser import BrowserView
from zope.security.checker import defineChecker, NamesChecker
from zope.component.view import provideView
from zope.component import getAdapter

from zope.app.interfaces.form import WidgetsError
from zope.app.component.metaconfigure import resolveInterface
from zope.app.form.utility import setUpEditWidgets, applyWidgetsChanges
from zope.app.browser.form.submit import Update
from zope.app.event import publish
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass

from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective, globalBrowserMenuService


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

    def __init__(self, context, request):
        super(EditView, self).__init__(context, request)

        self._setUpWidgets()

    def _setUpWidgets(self):
        adapted = getAdapter(self.context, self.schema)
        if adapted is not self.context:
            adapted = ContextWrapper(adapted, self.context, name='(adapted)')
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
                status = u"An error occured."
            else:
                setUpEditWidgets(self, self.schema, force=1,
                                 names=self.fieldNames)
                if changed:
                    status = "Updated %s" % datetime.utcnow()

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
                  NamesChecker(("__call__", "__getitem__", "browserDefault"),
                               permission))

    provideView(for_, name, IBrowserPresentation, class_, layer)


def normalize(_context, schema_, for_, class_, template, default_template,
              fields, omit, view=EditView):
    schema = resolveInterface(_context, schema_)

    if for_ is None:
        for_ = schema
    else:
        for_ = resolveInterface(_context, for_)

    if class_ is None:
        bases = view,
    else:
        # XXX What about class_.__implements__ ?
        bases = _context.resolve(class_), view

    if template is not None:
        template = _context.path(template)
        template = os.path.abspath(str(template))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)
    else:
        template = default_template



    names = getFieldNamesInOrder(schema)

    if fields:
        fields = fields.split()
        for name in fields:
            if name not in names:
                raise ValueError("Field name is not in schema",
                                 name, schema_)
    else:
        fields = names

    if omit:
        omit = omit.split()
        for name in omit:
            if name not in names:
                raise ValueError("Field name is not in schema",
                                 name, schema_)
        fields = [name for name in fields if name not in omit]

    return schema, for_, bases, template, fields

def edit(_context, name, schema, permission, label='',
         layer = "default",
         class_ = None, for_ = None,
         template = None, omit=None, fields=None,
         menu=None, title='Edit', usage=u''):

    if menu:
        actions = menuItemDirective(
            _context, menu, for_ or schema, '@@' + name, title,
            permission=permission)
    else:
        actions = []

    schema, for_, bases, template, fields = normalize(
        _context, schema, for_, class_, template, 'edit.pt', fields, omit)

    actions.append(
        Action(
        discriminator=('view', for_, name, IBrowserPresentation, layer),
        callable=EditViewFactory,
        args=(name, schema, label, permission, layer, template, 'edit.pt',
              bases, for_, fields, menu, usage),
        )
        )

    return actions

def subedit(_context, name, schema, label,
            permission='zope.Public', layer="default",
            class_=None, for_=None,
            template=None, omit=None, fields=None,
            fulledit=None, fulledit_label=None):

    schema, for_, bases, template, fields = normalize(
        _context, schema, for_, class_, template, 'subedit.pt', fields, omit)

    return [
        Action(
        discriminator=('view', for_, name, IBrowserPresentation, layer),
        callable=EditViewFactory,
        args=(name, schema, label, permission, layer, template, 'subedit.pt',
              bases, for_, fields, fulledit, fulledit_label),
        )
        ]
