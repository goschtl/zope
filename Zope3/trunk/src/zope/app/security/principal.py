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
"""These are the interfaces for the common fields.

$Id: principal.py,v 1.3 2003/02/11 15:59:55 sidnei Exp $
"""

from zope.exceptions import NotFoundError
from zope.component import getService
from zope.component.servicenames import Authentication

def checkPrincipal(context, principal_id):

    try:
        if getService(context, Authentication).getPrincipal(principal_id):
            return
    except NotFoundError:
        pass
    
    raise ValueError("Undefined principal id", principal_id)
