##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
$Id$
"""

from zope.app import zapi
from zope.app.security.permission import Permission
from zope.app.security.interfaces import IPermission

def addCheckerPublic():
    """Add the CheckerPublic permission as 'zope.Public'"""

    utilityService = zapi.getService(None, zapi.servicenames.Utilities)

    perm = Permission('zope.Public', 'Public',
            """Special permission used for resources that are always public

            The public permission is effectively an optimization, sine
            it allows security computation to be bypassed.
            """
            )
    utilityService.provideUtility(IPermission, perm, perm.id)
