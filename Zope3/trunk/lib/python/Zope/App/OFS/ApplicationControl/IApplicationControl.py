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
__doc__ = """ Application Control Interface

$Id: IApplicationControl.py,v 1.2 2002/06/10 23:27:51 jim Exp $"""

from Interface import Interface

class IApplicationControl(Interface):
    """ """

    def getStartTime():
        """Return the time when the ApplicationControl object has been instanciated
           in seconds since the epoch"""

    def registerView(name, title):
        """Register a view called <name> to be displayed in ApplicationControl
        """

    def getListOfViews():
        """Return a sequence containing dictionaries with the registered views' names
        and titles mapped with the keys 'name' and 'title'"""
