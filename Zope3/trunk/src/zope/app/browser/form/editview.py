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
$Id: editview.py,v 1.18 2003/04/11 22:15:45 gotcha Exp $
"""

from datetime import datetime

from zope.schema.interfaces import ValidationError
from zope.schema import getFieldNamesInOrder

from zope.configuration.action import Action
from zope.proxy.context import ContextWrapper
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.browser import BrowserView
from zope.security.checker import defineChecker, NamesChecker
from zope.component.view import provideView
from zope.component import queryAdapter

from zope.app.interfaces.form import WidgetsError
from zope.app.component.metaconfigure import resolveInterface
from zope.app.form.utility import setUpEditWidgets, getWidgetsData
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
        # XXX   This feels like it should be 'getAdapter';  it won't really
        #       be sensible to use an EditView against an object which
        #       doesn't implement our schema.  The AddView subclass, however,
        #       expects its context to be an IAdding, and doesn't use the
        #       schema attributes to set values.
        #
        #       I originally had EditView declare an '_adaptContextToSchema'
        #       method, which used 'getAdapter', and then overrode it in
        #       AddView to just return the context.  That felt icky, too,
        #       and was more complex, so I backed that out in favor of
        #       just using 'queryAdapter'.
        adapted = queryAdapter(context, self.schema)
        if adapted is not None:
            context = ContextWrapper(adapted, context, name='(adapted)')
        super(EditView, self).__init__(context, request)
        self._setUpWidgets()


    def _setUpWidgets(self):
        setUpEditWidgets(self, self.schema, names=self.fieldNames)

    def setPrefix(self, prefix):
        for widget in self.widgets():
            widget.setPrefix(prefix)

    def widgets(self):
        return [getattr(self, name)
                for name in self.fieldNames
                ]

    def apply_update(self, data):
        """Apply data updates

        Return true if data were unchanged and false otherwise.
        This sounds backwards, but it allows lazy implementations to
        avoid tracking changes.
        """

        content = self.context

        errors = []
        unchanged = True

        for name in data:
            try:
                newvalue = data[name]

                # We want to see if the data changes. Unfortunately,
                # we don't know enough to know that we won't get some
                # strange error, so we'll carefully ignore errors and
                # assume we should update the data if we can't be sure
                # it's the same.

                change = True

                # Use self as a marker
                change = getattr(content, name, self) != newvalue

                if change:
                    setattr(content, name, data[name])
                    unchanged = False

            except ValidationError, v:
                errors.append(v)

        if errors:
            raise WidgetsError(*errors)

        if not unchanged:
            publish(content, ObjectModifiedEvent(content))

        return unchanged

    def update(self):
        if self.update_status is not None:
            # We've been called before. Just return the status we previously
            # computed.
            return self.update_status

        status = ''
        
        if Update in self.request:
            unchanged = True
            try:
                data = getWidgetsData(self, self.schema,
                                      strict=False,
                                      set_missing=True,
                                      names=self.fieldNames,
                                      exclude_readonly=True)
                unchanged = self.apply_update(data)
            except WidgetsError, errors:
                self.errors = errors
                status = u"An error occured."
            else:
                setUpEditWidgets(self, self.schema, force=1,
                                 names=self.fieldNames)
                if not unchanged:
                    status = "Updated %s" % datetime.utcnow()

        self.update_status = status
        return status


def EditViewFactory(name, schema, label, permission, layer,
                    template, default_template, bases, for_, fields,
                    fulledit_path=None, fulledit_label=None, menu=u'',
                    usage=u''):
    # XXX What about the __implements__ of the bases?
    class_  = SimpleViewClass(
        template,
        used_for = schema, bases = bases
        )
    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields

    class_.fulledit_path = fulledit_path
    if fulledit_path and (fulledit_label is None):
        fulledit_label = "Full edit"

    class_.fulledit_label = fulledit_label

    class_.generated_form = ViewPageTemplateFile(default_template)

    class_.usage = usage or (
        menu and globalBrowserMenuService.getMenuUsage(menu)
        )

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__", "browserDefault"),
                    permission,
                    )
                  )

    provideView(for_, name, IBrowserPresentation, class_, layer)


def _normalize(_context, schema_, for_, class_, template, default_template,
               fields, omit, view=EditView):
    schema = resolveInterface(_context, schema_)

    if for_ is None:
        for_ = schema
    else:
        for_ = resolveInterface(_context, for_)

    if class_ is None:
        bases = (view, )
    else:
        # XXX What about class_.__implements__ ?
        bases = (_context.resolve(class_), view)


    if template is not None:
        template = _context.path(template)
    else:
        template = default_template

    template = str(template)

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


    (schema, for_, bases, template, fields,
     ) = _normalize(
        _context, schema, for_, class_, template, 'edit.pt', fields, omit)

    actions.append(
        Action(
        discriminator = ('view', for_, name, IBrowserPresentation, layer),
        callable = EditViewFactory,
        args = (name, schema, label, permission, layer, template, 'edit.pt',
                bases,
                for_, fields, menu, usage),
        )
        )

    return actions

def subedit(_context, name, schema, label,
              permission = 'zope.Public', layer = "default",
              class_ = None, for_ = None,
              template = None, omit=None, fields=None,
              fulledit=None, fulledit_label=None):

    (schema, for_, bases, template, fields,
     ) = _normalize(
        _context, schema, for_, class_, template, 'subedit.pt', fields, omit)

    return [
        Action(
        discriminator = ('view', for_, name, IBrowserPresentation, layer),
        callable = EditViewFactory,
        args = (name, schema, label, permission, layer, template, 'subedit.pt',
                bases,
                for_, fields, fulledit, fulledit_label),
        )
        ]
