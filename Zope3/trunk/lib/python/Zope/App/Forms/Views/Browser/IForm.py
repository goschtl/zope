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
$Id: IForm.py,v 1.1 2002/07/16 15:15:54 srichter Exp $
"""
from Zope.Publisher.Browser import IBrowserView 
from Interface.Attribute import Attribute


class IReadForm(IBrowserView):

    custom_widgets = Attribute(""" """)

    def getWidgetForFieldId(id):
        """"""

    def getWidgetForField(field):
        """Return the correct widget instance for a field. This method
        consildates the custom_widgets attribute """


    def action():
        """Execute the form. By default it tries to save the values back
           into the content object."""


class IWriteForm(IBrowserView):

    def getFieldData():
        """ """
        
    def saveValuesInContext(mapping):
        """Store all the new data inside the context object."""


class IForm(IReadForm, IWriteForm):
