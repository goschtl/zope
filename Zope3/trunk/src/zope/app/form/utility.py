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

$Id: utility.py,v 1.26 2004/03/05 22:09:06 jim Exp $
"""
__metaclass__ = type

from warnings import warn
from zope.component import getView, getDefaultViewName
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import ValidationError
from zope.app.interfaces.form import IWidget
from zope.app.interfaces.form import WidgetsError, MissingInputError
from zope.app.interfaces.form import InputErrors
from zope.component.interfaces import IViewFactory

def _fieldlist(names, schema):
    if not names:
        fields = getFieldsInOrder(schema)
    else:
        fields = [ (name, schema[name]) for name in names ]
    return fields

def _whine(view, name):
    url = view.request.URL
    vname = view.__class__.__name__
    warn(
        "View (%s) saved a widget (%s) without a '_widget' suffix.\n"
        "Url: %s"
        % (vname, name, url),
        DeprecationWarning, stacklevel=4,
        )

class WhiningWidget:

    def __init__(self, view, name, widget):
        self.__widget = widget
        self.__whineargs = view, name

    def __whine(self):
        whineargs = self.__whineargs
        if whineargs:
            _whine(*whineargs)
            self.__whineargs = ()

    def __call__(self, *args, **kw):
        self.__whine()
        return self.__widget(*args, **kw)

    def __repr__(self):
        self.__whine()
        return `self.__widget`

    def __str__(self):
        self.__whine()
        return str(self.__widget)

    def __getattr__(self, name):
        self.__whine()
        return getattr(self.__widget, name)

def setUpWidget(view, name, field, value=None, prefix=None,
                force=False, vname=None, context=None):
    """Set up a single view widget

    The widget will be an attribute of the view. If there is already
    an attribute of the given name, it must be a widget and it will be
    initialized with the given value if not None.

    If there isn't already a view attribute of the given name, then a
    widget will be created and assigned to the attribute.
    """
    # Has a (custom) widget already been defined?

    wname = name+'_widget'

    widget = getattr(view, wname, None)
    installold = False
    if widget is None:
        widget = getattr(view, name, None)
        if widget is not None:
            if IViewFactory.providedBy(widget):
                # Old custom widget definition.
                # We'll accept it, but we'll whine
                _whine(view, name)

                # we also need to remember to install the widget
                installold = True
            elif IWidget.providedBy(widget):
                # Old widget definition. We'll accept it, but we'll whine
                _whine(view, name)
            else:
                # we found something else, which is innocent.
                widget = None
                installold = True

    if context is None:
        context = view.context

    if widget is None:
        # There isn't already a widget, create one
        field = field.bind(context)
        if vname is None:
            vname = getDefaultViewName(field, view.request)
        widget = getView(field, vname, view.request)
        setattr(view, wname, widget)
        if not hasattr(view, name):
            setattr(view, name, WhiningWidget(view, name, widget))

    else:
        # We have an attribute of the right name, is it really a widget
        if IViewFactory.providedBy(widget):
            # This is a view factory, probably a custom widget.
            # Try to make it into a widget.
            field = field.bind(context)
            widget = widget(field, view.request)
            if IWidget.providedBy(widget):
                # Yee ha! We have a widget now, save it
                setattr(view, wname, widget)
                if installold or not hasattr(view, name):
                    setattr(view, name, WhiningWidget(view, name, widget))

        if not IWidget.providedBy(widget):
            raise TypeError(
                "The %s view attribute named, %s, should be a widget, "
                "but isn't."
                % (view.__class__.__name__, name))

        if not hasattr(view, wname):
            setattr(view, wname, widget)

    if prefix:
        widget.setPrefix(prefix)

    if force or not widget.hasInput() and value is not None:
        # XXX: The doc string sez value should not be None; maybe it should not 
        # be field.missing_value instead?
        widget.setRenderedValue(value)


def setUpWidgets(view, schema, prefix=None, force=False,
                 initial={}, names=None, context=None):
    """Set up widgets for the fields defined by a schema

    """
    for (name, field) in _fieldlist(names, schema):
        setUpWidget(view, name, field, initial.get(name),
                    prefix=prefix, force=force, context=context)


def setUpEditWidgets(view, schema, content=None, prefix=None, force=False,
                     names=None, context=None):
    """Set up widgets for the fields defined by a schema

    Initial data is provided by content object attributes.
    No initial data is provided if the content lacks a named
    attribute, or if the named attribute value is None.
    """
    _setUpWidgets(view, schema, content, prefix, force,
                  names, context, 'display', 'edit')

def setUpDisplayWidgets(view, schema, content=None, prefix=None, force=False,
                        names=None, context=None):
    """Set up widgets for the fields defined by a schema

    Initial data is provided by content object attributes.
    No initial data is provided if the content lacks a named
    attribute, or if the named attribute value is None.
    """
    _setUpWidgets(view, schema, content, prefix, force,
                  names, context, 'display', 'display')

def _setUpWidgets(view, schema, content, prefix, force,
                  names, context, displayname, editname):
    # Set up widgets for the fields defined by a schema.
    #
    # displayname is the name of the view used for a field that is
    # marked read-only; editname is the name of the view used for a
    # field that is editable.
    #
    # Initial data is provided by content object attributes.
    # No initial data is provided if the content lacks a named
    # attribute, or if the named attribute value is None.
    #
    if content is None:
        if context is None:
            content = view.context
        else:
            content = context

    for name, field in _fieldlist(names, schema):
        if field.readonly:
            vname = displayname
        else:
            vname = editname

        try:
            value = field.get(content)
        except AttributeError, v:
            if v.__class__ != AttributeError:
                raise
            value = None

        setUpWidget(view, name, field, value,
                    prefix=prefix, force=force, vname=vname, context=context)

def viewHasInput(view, schema, names=None):
    """Check if we have any user-entered data defined by a schema.

    Returns True if any schema field related widget has input provided by 
    the user.
    """
    for name, field in _fieldlist(names, schema):
        if  getattr(view, name+'_widget').hasInput():
            return True
    return False

def applyWidgetsChanges(view, content, schema, strict=True,
        names=None, set_missing=True, do_not_raise=False,
        exclude_readonly=False):
    """Apply changes in widgets to the object.
    
    XXX this needs to be thoroughly documented.
    """
    errors = []
    changed = False
    for name, field in _fieldlist(names, schema):
        widget = getattr(view, name+'_widget')
        if exclude_readonly and field.readonly:
            continue
        if widget.hasInput():
            try:
                changed = widget.applyChanges(content) or changed
            except InputErrors, v:
                errors.append(v)

    if errors and not do_not_raise:
        raise WidgetsError(*errors)

    return changed

def getWidgetsData(view, schema, strict=True, names=None, set_missing=True,
                   do_not_raise=False, exclude_readonly=False):
    """Collect the user-entered data defined by a schema

    Data is collected from view widgets. For every field in the
    schema, we look for a view of the same name and get it's data.

    The data are returned in a mapping from field name to value.

    If the strict argument is true, then all of the data defined by
    the schema will be returned. If some required data are missing
    from the input, an error will be raised.

    If set_missing is true and the widget has no data, then the
    field's value is set to its missing value.  Otherwise, a widget
    with no data is ignored. (However, if that field is required and
    strict is true, an error will be raised.)

    E.g., a typical text line widget should have a min_length of 1,
    and if it is required, it has got to have something in, otherwise
    WidgetsError is raised.  If it's not required and it's empty, its
    value will be the appropriate missing value.  Right now this is
    hardcoded as None, but it should be changed so the field can
    provide it as an empty string.

    do_not_raise is used if a call to getWidgetsData raises an exception,
    and you want to make use of the data that *is* available in your
    error-handler.

    Normally, readonly fields are included. To exclude readonly fields,
    provide a exclude_readonly keyword argument with a true value.

    """

    result = {}
    errors = []

    for name, field in _fieldlist(names, schema):
        widget = getattr(view, name+'_widget')
        if exclude_readonly and widget.context.readonly:
            continue
        if widget.hasInput():
            try:
                result[name] = widget.getInputValue()
            except InputErrors, v:
                errors.append(v)
        elif strict and field.required:
            errors.append(MissingInputError(name, widget.title,
                                            'the field is required')
                          )
        elif set_missing:
            result[name] = field.missing_value

    if errors and not do_not_raise:
        raise WidgetsError(*errors)

    return result

def getWidgetsDataForContent(view, schema, content=None, strict=True,
                             names=None, set_missing=True):
    """Collect the user-entered data defined by a schema

    Data is collected from view widgets. For every field in the
    schema, we look for a view of the same name and get it's data.

    The data are assigned to the given content object.

    If the strict argument is true, then if some required data are
    missing from the input, an error will be raised.

    If set_missing is true and the widget has no data, then the
    field's value is set to its missing value.  Otherwise, a widget
    with no data is ignored. (However, if that field is required and
    strict is true, an error will be raised.)

    If the strict argument is true, then all of the data defined by
    the schema will be set, at least for required fields. If some data
    for required fields are missing from the input, an error will be
    raised.

    """
    data = getWidgetsData(view, schema, strict, names)

    if content is None:
        content = view.context

    errors = []

    for name in data:
        try:
            field = schema[name]
            field.set(content, data[name])
        except ValidationError, v:
            errors.append(v)

    if errors:
        raise WidgetsError(*errors)

def getWidgetsDataFromAdapter(adapter, schema, strict=True,
                              names=None, set_missing=True,
                              do_not_raise=True):
    """Collect the user-entered data defined by a schema

    Data is collected from adapter properties. For every field in the
    schema, we look for a property of the same name and get it's data.

    The data are returned in a mapping from field name to value.

    If the strict argument is true, then all of the data defined by
    the schema will be returned. If some required data are missing
    from the input, an error will be raised.

    If set_missing is true and the widget has no data, then the
    field's value is set to its missing value.  Otherwise, a widget
    with no data is ignored. (However, if that field is required and
    strict is true, an error will be raised.)

    E.g., a typical text line widget should have a min_length of 1,
    and if it is required, it has got to have something in, otherwise
    WidgetsError is raised.  If it's not required and it's empty, its
    value will be the appropriate missing value.  Right now this is
    hardcoded as None, but it should be changed so the field can
    provide it as an empty string.

    do_not_raise is used if a call to getWidgetsData raises an exception,
    and you want to make use of the data that *is* available in your
    error-handler.
    """

    result = {}
    errors = []

    for name, field in _fieldlist(names, schema):
        prop = getattr(adapter, name, None)
        if prop is not None:
            if callable(prop):
                value = prop()
            else:
                value = prop
            result[name] = value
        elif strict and field.required:
            errors.append(MissingInputError(name, name,
                                            'the field is required'))
        elif set_missing:
            result[name] = field.missing_value

    if errors and not do_not_raise:
        raise WidgetsError(*errors)

    return result
