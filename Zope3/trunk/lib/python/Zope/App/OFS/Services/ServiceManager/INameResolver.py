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
$Id: INameResolver.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from Interface import Interface

class INameResolver(Interface):
    """Objects that can resolve dotted names to objects
    """

    def resolve(dotted_name):
        """Resolve the given dotted name to a module global variable.

        If the name ends with a trailing dot, the last name segment
        may be repeated.
        """

__doc__ = INameResolver.__doc__ + __doc__
