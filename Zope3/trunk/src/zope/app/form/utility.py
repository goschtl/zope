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
"""Form utility functions

In Zope 2's formulator, forms provide a basic mechanism for
organizing collections of fields and providing user interfaces for
them, especially editing interfaces.

In Zope 3, formulator's forms are replaced by Schema (See
zope.schema). In addition, the Formulator fields have been replaced by
schema fields and form widgets. Schema fields just express the sematics
of data values. They contain no presentation logic or parameters.
Widgets are views on fields that take care of presentation. The widget
view names represent styles that can be selected by applications to
customise the presentation. There can also be custom widgets with
specific parameters.

This module provides some utility functions that provide some of the
functionality of formulator forms that isn't handled by schema,
fields, or widgets.

$Id: utility.py,v 1.5 2003/01/25 18:30:05 stevea Exp $
"""
__metaclass__ = type

from zope.component import getView, getDefaultViewName
from zope.schema.interfaces import IField, ValidationError
from zope.app.interfaces.form import IWidget
from zope.app.interfaces.form import WidgetsError, MissingInputError
from zope.app.interfaces.form import InputErrors
from zope.component.interfaces import IViewFactory


def setUpWidget(view, name, field, value=None, prefix=None,
                force=0, vname=None):
    """Set up a single view widget

    The widget will be an attribute of the view. If there is already
    an attribute of the given name, it must be a widget and it will be
    initialized with the given value if not None.

    If there isn't already a view attribute of the given name, then a
    widget will be created and assigned to the attribute.
    """

    # Has a (custom) widget already been defined?
    widget = getattr(view, name, None)

    if widget is None:
        # There isn't already a widget, create one
        field = field.bind(view.context)
        if vname is None:
            vname = getDefaultViewName(field, view.request)
        widget = getView(field, vname, view.request)
        setattr(view, name, widget)

    else:
        # We have an attribute of the right name, is it really a widget
        if IViewFactory.isImplementedBy(widget):
            # This is a view factory, probably a custom widget.
            # Try to make it into a widget.
            field = field.bind(view.context)
            widget = widget(field, view.request)
            if IWidget.isImplementedBy(widget):
                # Yee ha! We have a widget now, save it
                setattr(view, name, widget)

        if not IWidget.isImplementedBy(widget):
            raise TypeError(
                "The %s view attribute named, %s, should be a widget, "
                "but isn't."
                % (view.__class__.__name__, name))

    if prefix:
        widget.setPrefix(prefix)

    if value is not None and (force or not widget.haveData()):
        widget.setData(value)

def fieldNames(schema):

    names = []
    for name in schema:
        field = schema[name]
        if IField.isImplementedBy(field):
            names.append((field.order, name))

    names.sort()

    return [name[1] for name in names]

def setUpWidgets(view, schema, prefix=None, force=0,
                 initial={}, names=None):
    """Set up widgets for the fields defined by a schema

    """

    for name in (names or schema):
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            setUpWidget(view, name, field, initial.get(name),
                        prefix=prefix, force=force)

def setUpEditWidgets(view, schema, content=None, prefix=None, force=0,
                     names=None):
    """Set up widgets for the fields defined by a schema

    Initial data is provided by content object attributes.
    No initial data is provided if the content lacks a named
    attribute, or if the named attribute value is None.
    """
    if content is None:
        content = view.context

    for name in (names or schema):
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            if field.readonly:
                vname = 'display'
            else:
                vname = 'edit'

            try:
                value = getattr(content, name)
            except AttributeError, v:
                if v.__class__ != AttributeError:
                    raise
                value = None

            setUpWidget(view, name, field, value,
                        prefix = prefix, force = force, vname = vname)

def haveWidgetsData(view, schema, names=None):
    """Collect the user-entered data defined by a schema

    Data is collected from view widgets. For every field in the
    schema, we look for a view of the same name and get it's data.

    The data are returned in a mapping from field name to value.
    """

    for name in (names or schema):
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            if  getattr(view, name).haveData():
                return True

    return False

def getWidgetsData(view, schema, required=1, names=None):
    """Collect the user-entered data defined by a schema

    Data is collected from view widgets. For every field in the
    schema, we look for a view of the same name and get it's data.

    The data are returned in a mapping from field name to value.

    If the required argument is true, then all of the data defined by
    the schema will be returned. If some required data are missing
    from the input, an error will be raised.

    """

    result = {}
    errors = []

    for name in (names or schema):
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            widget = getattr(view, name)
            if widget.haveData():
                try:
                    result[name] = widget.getData()
                except InputErrors, v:
                    errors.append(v)
            elif required and field.required:
                raise MissingInputError(
                    widget.name, widget.title, name)

    if errors:
        raise WidgetsError(*errors)

    return result

def getWidgetsDataForContent(view, schema, content=None, required=0,
                             names=None):
    """Collect the user-entered data defined by a schema

    Data is collected from view widgets. For every field in the
    schema, we look for a view of the same name and get it's data.

    The data are assigned to the given content object.

    If the required argument is true, then all of the data defined by
    the schema will be set, at least for required fields. If some data
    for required fields are missing from the input, an error will be
    raised.

    """

    data = getWidgetsData(view, schema, required, names)

    if content is None:
        content = view.context

    errors = []

    for name in data:
        # OK, we really got a field
        try:
            setattr(content, name, data[name])
        except ValidationError, v:
            errors.append(v)

    if errors:
        raise WidgetsError(*errors)
