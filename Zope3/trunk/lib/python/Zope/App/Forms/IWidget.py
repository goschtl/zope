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
$Id: IWidget.py,v 1.5 2002/11/11 20:52:57 jim Exp $
"""
from Zope.ComponentArchitecture.IView import IView
from Interface.Attribute import Attribute

class IWidget(IView):
    """Generically describes the behavior of a widget.

    The widget defines a list of propertyNames, which describes
    what properties of the widget are available to use for
    constructing the widget render output.

    Note that this level must be still presentation independent.
    """

    propertyNames = Attribute("""This is a list of attributes that are
                                 defined for the widget.""")

    def getValue(name):
        """Look up a Widget setting (value) by name."""

    def getData():
        """Return converted and validated widget data.

        If there is no user input and the field is required, then a
        MissingInputError will be raised.

        If there is no user input and the field is not required, then
        the field default value will be returned.

        A WidgetInputError is returned in the case of one or more
        errors encountered, inputting, converting, or validating the data.
        """

    def haveData():
        """Is there input data for the field

        Return True if there is data and False otherwise.
        """

    name = Attribute("""The uniquewidget name

        This must be unique within a set of widgets.
        """)

    title = Attribute("The widget title")

    required = Attribute("Flag indicating whether the field is required")
    
    def setData(value):
        """Set the default data for the widget.

        The given value should be used even if the user has entered
        data.
        """
