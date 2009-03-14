##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Backward-compatibility imports for the global principal registry

$Id$
"""

# BBB: these were moved to zope.principalregistry
from zope.principalregistry.principalregistry import (
    DuplicateLogin,
    DuplicateId,
    PrincipalRegistry,
    principalRegistry,
    PrincipalBase,
    Group,
    Principal,
    UnauthenticatedPrincipal,
    fallback_unauthenticated_principal,
    UnauthenticatedGroup,
    AuthenticatedGroup,
    EverybodyGroup,
    )
