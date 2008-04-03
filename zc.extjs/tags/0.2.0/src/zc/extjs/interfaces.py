##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import zope.app.form.interfaces
import zope.interface
import zope.publisher.interfaces.browser

class IAjaxRequest(zope.publisher.interfaces.browser.IBrowserRequest):
    """Ajax requests
    """

class IInputWidget(zope.app.form.interfaces.IInputWidget):
    """Ajax widgets

    Ajax widgets work much like browser widgets except that rather
    than rendering HTML, they render ExtJS widget configurations.    
    """

    def js_config(self):
        """Return an ExtJS widget configuration

        The return value is a dictionary containing data needed to
        create an ExtJS field.

        The resule may contain a widget_constructor property
        containing the name of a Javascript to be used to build the
        widget, in which case the data is passed to the Javascript function.

        If rendered data have been set, the output should contain a
        value property.

        The output must contain name and id properties.
        """

    def formValue(v):
        """Return a value suitable to passing to a Ext field setValue method

        This will typically be a string.  None may be returned if the
        value passed in is a missing value.
        """

    def value(raw):
        """Convert a raw value, from a form, to an application value
        """

