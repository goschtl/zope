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
$Id: IWidget.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from Zope.ComponentArchitecture.IContextDependent import IContextDependent
from Interface.Attribute import Attribute

class IWidget(IContextDependent):
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
