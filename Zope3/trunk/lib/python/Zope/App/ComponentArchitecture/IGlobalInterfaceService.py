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
$Id: IGlobalInterfaceService.py,v 1.2 2002/11/19 23:15:14 jim Exp $
"""

from IInterfaceService import IInterfaceService

class IGlobalInterfaceService(IInterfaceService):
    """Global registry for Interface
    """

    def provideInterface(id, interface):
        """Register an interface with a given id

        The id is the full dotted name for the interface.
        """

__doc__ = IGlobalInterfaceService.__doc__ + __doc__
