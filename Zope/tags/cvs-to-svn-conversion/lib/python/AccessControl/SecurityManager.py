##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
'''API module to set the security policy


$Id: SecurityManager.py,v 1.15 2004/01/15 23:09:03 tseaver Exp $'''

from AccessControl import ImplPython as _ImplPython
from AccessControl.SimpleObjectPolicies import _noroles


def setSecurityPolicy(aSecurityPolicy):
    """Set the system default security policy.

    This method should only be caused by system startup code. It should
    never, for example, be called during a web request.
    """
    last = _ImplPython._defaultPolicy
    _ImplPython._defaultPolicy = aSecurityPolicy
    return last


# AccessControl.Implementation inserts SecurityManager.
