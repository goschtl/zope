##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces needed by the module service.

XXX There is no module service yet; instead, the service manager
currently implements it.  This should change.

$Id: module.py,v 1.1 2003/03/13 17:10:36 gvanrossum Exp $
"""

from zope.interface import Interface

class IModuleService(Interface):
    """Objects that can resolve dotted names to objects
    """

    def resolve(dotted_name):
        """Resolve the given dotted name to a module global variable.

        If the name ends with a trailing dot, the last name segment
        may be repeated.

        If the dotted name cannot be resolved, an ImportError is raised.
        """
