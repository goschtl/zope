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
$Id: IForm.py,v 1.5 2002/07/17 18:43:41 srichter Exp $
"""
from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Interface.Attribute import Attribute

class IReadForm(IBrowserView):
    """This interface defines methods and attributes that are required to
    display a form."""

    form = Attribute(
        """The form template. Usually a Page Template.""")

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

    def getWidgetForFieldId(id):
        """Lookup the widget of the field having id."""

    def getWidgetForField(field):
        """Return the correct widget instance for a field. This method
        consildates the custom_widgets attribute """

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
