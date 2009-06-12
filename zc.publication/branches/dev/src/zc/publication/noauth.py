##############################################################################
#
# Copyright Zope Foundation and Contributors.
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
"""Never authenticate.

This is a suitable plugin for apps that don't support login.
"""

import zope.authentication.interfaces
import zope.principalregistry.principalregistry

def authenticate(request):
    pass


def unauthenticatedPrincipal():
    return zope.principalregistry.principalregistry.UnauthenticatedPrincipal(
        '', 'Unauthenticated', 'No one can authenticate')

def unauthorized(id, request):
    pass

def getPrincipal(id):
    if id == '':
        return unauthenticatedPrincipal()
    raise zope.authentication.interfaces.PrincipalLookupError(id)
