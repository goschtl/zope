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
organizating collections of fields and providing unsert interfaces for
them, especially editing interfaces.

In Zope 3, formulator's forms are replaced by Schema (See
Zope.Schema). In addition, the Formulator fields have been replaced by
schema fields and form widgets. Schema fields just express the sematics
of data values. They contain no presentation logic or parameters.
Widgets are views on fields that take care of presentation. The widget
view names represent styles that can be selected by applications to
customise the presentation. There can also be custom widgets with
specific parameters.

This module provides some utility functions that provide some of the
functionality of formulator forms that isn't handled by schema,
fields, or widgets.

$Id: Utility.py,v 1.4 2002/10/30 09:19:20 stevea Exp $
"""
__metaclass__ = type

from Zope.ComponentArchitecture import getView, getDefaultViewName
from Zope.Schema.IField import IField
from Zope.App.Forms.IWidget import IWidget
from Zope.App.Forms.Exceptions import WidgetsError
from Zope.Proxy.ContextWrapper import ContextWrapper


def setUpWidget(view, name, field, value=None, prefix=None):
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
        field = ContextWrapper(field, view.context, name=name)
        vname = getDefaultViewName(field, view.request)
        widget = getView(field, vname, view.request)
        setattr(view, name, widget)
    else:
        # We have an attribute of the right name, it it really a widget
        if not IWidget.isImplementedBy(widget):
            raise TypeError(
                "The %s view attribute named, %s, should be a widget, "
                "but isn't."
                % (view.__class__.__name__, name))

    if prefix:
        widget.setPrefix(prefix)

    if value is not None:
        widget.setData(value)

def setUpWidgets(view, schema, prefix=None, **kw):
    """Set up widgets for the fields defined by a schema

    Initial data is provided by keyword arguments.
    """
    
    for name in schema:
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            setUpWidget(view, name, field, kw.get(name), prefix=prefix)

def setUpEditWidgets(view, schema, content=None, prefix=None):
    """Set up widgets for the fields defined by a schema

    Initial data is provided by content object attributes.
    No initial data is provided if the content lacks a named
    attribute, or if the named attribute value is None.
    """
    if content is None:
        content = view.context

    for name in schema:
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            setUpWidget(view, name, field, getattr(content, name, None),
                        prefix = prefix)

def getWidgetsData(view, schema):
    """Collect the user-entered data defined by a schema

    Data is collected from view widgets. For every field in the
    schema, we look for a view of the same name and get it's data.

    The data are returned in a mapping from field name to value.
    """

    result = {}
    errors = []

    for name in schema:
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            try:
                result[name] = getattr(view, name).getData()
            except Exception, v:
                errors.append(v)

    if errors:
        raise WidgetsError(*errors)
    
    return result

def getWidgetsDataForContent(view, schema, content=None):
    """Collect the user-entered data defined by a schema

    Data is collected from view widgets. For every field in the
    schema, we look for a view of the same name and get it's data.

    The data are assigned to the given content object.
    """
    data = getWidgetsData(view, schema)
    
    if content is None:
        content = view.context

    for name in schema:
        field = schema[name]
        if IField.isImplementedBy(field):
            # OK, we really got a field
            setattr(content, name, getattr(view, name).getData())

