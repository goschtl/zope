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
$Id: globalinterfaceservice.py,v 1.2 2002/12/25 14:12:58 jim Exp $
"""

from zope.app.component.globalinterfaceservice import IInterfaceService

class IGlobalInterfaceService(IInterfaceService):
    """Global registry for Interface
    """

    def provideInterface(id, interface):
        """Register an interface with a given id

        The id is the full dotted name for the interface.

        If the id is false, the id will be computed from the interface
        module and name.

        """

__doc__ = IGlobalInterfaceService.__doc__ + __doc__
