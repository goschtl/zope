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
$Id: IUnauthenticatedPrincipal.py,v 1.1 2002/07/15 22:01:10 jim Exp $
"""

from IPrincipal import IPrincipal

class IUnauthenticatedPrincipal(IPrincipal):
    """A principal that hasn't been authenticated.

    Authenticated principals are preferable to UnauthenticatedPrincipals.
    """

__doc__ = IUnauthenticatedPrincipal.__doc__ + __doc__
