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
$Id: add.py,v 1.5 2003/01/09 14:13:04 jim Exp $
"""

import sys

from zope.schema.interfaces import ValidationError

from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.interfaces.form import WidgetsError
from zope.app.form.utility import setUpWidgets, getWidgetsData
from zope.app.form.utility import haveWidgetsData, fieldNames
from zope.configuration.action import Action
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.checker import defineChecker, NamesChecker
from zope.component.view import provideView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.browser.form.submit import Update
from zope.app.browser.form.editview import EditView, _normalize
from zope.app.interfaces.container import IAdding

class AddView(EditView):
    """Simple edit-view base class

    Subclasses should provide a schema attribute defining the schema
    to be edited.
    """

    def __init__(self, context, request):
        super(EditView, self).__init__(context, request)
        setUpWidgets(self, self.schema, names=self.fieldNames)

    def apply_update(self, data):
        """Apply data updates

        Return true if data were unchanged and false otherwise.
        This sounds backwards, but it allows lazy implementations to
        avoid tracking changes.
        """

        args = []
        for name in self._arguments:
            args.append(data[name])

        kw = {}
        for name in self._keyword_arguments:
            if name in data:
                kw[str(name)] = data[name]

        content = self._factory(*args, **kw)

        errors = []

        for name in self._set_before_add:
            if name in data:
                try:
                    setattr(content, name, data[name])
                except ValidationError:
                    errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        publish(content, ObjectCreatedEvent(content))

        content = self.context.add(content)

        for name in self._set_after_add:
            if name in data:
                try:
                    setattr(content, name, data[name])
                except ValidationError:
                    errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        return content

    def update(self):
        if Update in self.request:
            try:
                data = getWidgetsData(self, self.schema,
                                      required=0, names=self.fieldNames)
                content = self.apply_update(data)
            except WidgetsError, errors:
                self.errors = errors
                return u"An error occured."

            self.request.response.redirect(self.context.nextURL())


def AddViewFactory(name, schema, label, permission, layer,
                   template, default_template, bases, for_,
                   fields, content_factory, arguments,
                   keyword_arguments, set_before_add, set_after_add):

    class_  = SimpleViewClass(
        template,
        used_for = schema, bases = bases
        )

    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields
    class_._factory = content_factory
    class_._arguments = arguments
    class_._keyword_arguments = keyword_arguments
    class_._set_before_add = set_before_add
    class_._set_after_add = set_after_add

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__", "browserDefault"),
                    permission,
                    )
                  )

    provideView(for_, name, IBrowserPresentation, class_, layer)

def add(_context, name, schema, label, content_factory,
        permission = 'zope.Public', layer = "default",
        class_ = None, for_ = None,
        template = None, omit=None, fields=None,
        arguments='', keyword_arguments='',
        set_before_add='', set_after_add=''):

    content_factory = _context.resolve(content_factory)

    (schema, for_, bases, template, fields,
     ) = _normalize(
        _context, schema, for_, class_, template, 'add.pt', fields, omit,
        AddView)

    leftover = fields

    if arguments:
        arguments = arguments.split()
        missing = [n for n in arguments if n not in fields]
        if missing:
            raise ValueError("Some arguments are not included in the form",
                             missing)
        leftover = [n for n in leftover if n not in arguments]

    if keyword_arguments:
        keyword_arguments = keyword_arguments.split()
        missing = [n for n in keyword_arguments if n not in fields]
        if missing:
            raise ValueError(
                "Some keyword_arguments are not included in the form",
                missing)
        leftover = [n for n in leftover if n not in keyword_arguments]

    if set_before_add:
        set_before_add = set_before_add.split()
        missing = [n for n in set_before_add if n not in fields]
        if missing:
            raise ValueError(
                "Some set_before_add are not included in the form",
                missing)
        leftover = [n for n in leftover if n not in set_before_add]

    if set_after_add:
        set_after_add = set_after_add.split()
        missing = [n for n in set_after_add if n not in fields]
        if missing:
            raise ValueError(
                "Some set_after_add are not included in the form",
                missing)
        leftover = [n for n in leftover if n not in set_after_add]

        set_after_add += leftover

    else:

        set_after_add = leftover

    return [
        Action(
        discriminator = ('http://namespaces.zope.org/form/add', name, layer),
        callable = AddViewFactory,
        args = (name, schema, label, permission, layer, template, 'add.pt',
                bases,
                IAdding, fields, content_factory, arguments,
                keyword_arguments, set_before_add, set_after_add),
        )
        ]
