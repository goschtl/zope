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
"""
$Id: form.py,v 1.5 2003/01/16 19:53:09 stevea Exp $
"""
from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IBrowserView
from zope.app.interfaces.form import IWidget


class IReadForm(IBrowserView):
    """This interface defines methods and attributes that are required to
    display a form."""

    form = Attribute(
        """The form template. Usually a Page Template.""")

    schema = Attribute(
        """The schema this form should be constructed from.""")

    custom_widgets = Attribute(
        """A dictionary that holds custom widgets for various fields.""")

    fields_order = Attribute(
        """A list that contains the field ids in the order they should
        be displayed. If the value of this attribute is None, then the
        fields are just grapped randomly out of the various schemas.

        Furthermore, if fields are specified then only these fields are
        used for the form, not all that could be possibly found.
        """)

    def getFields():
        """Get all the fields that need input from the content object."""

    def getField(name):
        """Get a field by name from the content object schemas."""

    def getWidgetForFieldName(name):
        """Lookup the widget of the field by name."""

    def getWidgetForField(field):
        """Return the correct widget instance for a field. This method
        consults the custom_widgets attribute """

    def renderField(field):
        """Render a field using the widgets."""

    def action():
        """Execute the form. By default it tries to save the values back
           into the content object."""


class IWriteForm(IBrowserView):
    """This interface defines methods and attributes that are required to
    retrieve the data from the request and store them back into the."""

    def saveValuesInContext():
        """This method is responsible of retrieving all the data from
        the request, converting it, validating it and then store it back
        to the context object."""


class IForm(IReadForm, IWriteForm):
    """This is a complete form."""


class IBrowserWidget(IWidget):
    """A field widget contains all the properties that are required
       to represent a field. Properties include css_sheet,
       default value and so on.
    """

    def setPrefix(self, prefix):
        """Set the form-variable name prefix used for the widget

        The widget will define it's own form variable names by
        concatinating the profix and the field name using a dot. For
        example, with a prefix of "page" and a field name of "title",
        a form name of "page.title" will be used. A widget may use
        multiple form fields. If so, it should add distinguishing
        suffixes to the prefix and field name.
        """

    def __call__():
        """Render the widget
        """

    def hidden():
        """Render the widget as a hidden field
        """

    def label():
        """Render a label tag"""

    def row():
        """Render the widget as two div elements, for the label and the field.

        For example:
          <div class="label">label</div><div class="field">field</div>
        """

    # XXX The following two methods are being supported for backward
    # compatability. They are deprecated and will be refactored away
    # eventually.

    def render(value):
        """Renders this widget as HTML using property values in field.

        The value if given will be used as the default value for the widget.
        """

    def renderHidden(value):
        """Renders this widget as a hidden field.
        """


class IFormCollaborationView(Interface):
    """Views that collaborate to create a single form

    When a form is applied, the changes in the form need to
    be applied to individual views, which update objects as
    necessary.
    """

    def __call__():
        """Render the view as a part of a larger form.

        Form input elements should be included, prefixed with the
        prefix given to setPrefix.

        'form' and 'submit' elements should not be included. They
        will be provided for the larger form.
        """

    def setPrefix(prefix):
        """Set the prefix used for names of input elements

        Element names should begin with the given prefix,
        followed by a dot.
        """

    def update():
        """Update the form with data from the request.
        """
