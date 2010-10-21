##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Session Widget Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.app.form import interfaces

class ISessionWidget(interfaces.IInputWidget):
    """A widget that communicates its data via a session."""

    session = zope.interface.Attribute(
        '''The session object that holds all information necessary for the
        session widget to implement the IWidget API. Two fields are declared:

        ``data`` -- Holds the data object that is to be stored. It can be any
                    arbitrary Python object.

        ``changed`` -- a flag (boolean) describing whether the object has been
                       changed since the widget was originally initialized.
        ''')

class ISessionWidgetForm(zope.interface.Interface):
    """Marker interface for forms used in session widgets"""
    
    
