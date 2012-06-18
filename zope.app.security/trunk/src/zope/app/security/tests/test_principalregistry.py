##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Global Authentication Serive or Principal Registry Tests

$Id$
"""
import unittest
from zope.testing import doctest

def test_bbb_imports():
    """
    Let's check that principal registry that was moved to
    zope.principalregistry is still importable from original places.

      >>> import zope.app.security.principalregistry as old
      >>> import zope.principalregistry.principalregistry as new

      >>> old.DuplicateLogin is new.DuplicateLogin
      True
      >>> old.DuplicateId is new.DuplicateId
      True
      >>> old.PrincipalRegistry is new.PrincipalRegistry
      True
      >>> old.principalRegistry is new.principalRegistry
      True
      >>> old.PrincipalBase is new.PrincipalBase
      True
      >>> old.Group is new.Group
      True
      >>> old.Principal is new.Principal
      True
      >>> old.UnauthenticatedPrincipal is new.UnauthenticatedPrincipal
      True
      >>> old.fallback_unauthenticated_principal is new.fallback_unauthenticated_principal
      True
      >>> old.UnauthenticatedGroup is new.UnauthenticatedGroup
      True
      >>> old.AuthenticatedGroup is new.AuthenticatedGroup
      True
      >>> old.EverybodyGroup is new.EverybodyGroup
      True

      >>> import zope.app.security.metadirectives as old
      >>> import zope.principalregistry.metadirectives as new

      >>> old.IBasePrincipalDirective is new.IBasePrincipalDirective
      True
      >>> old.IDefinePrincipalDirective is new.IDefinePrincipalDirective
      True
      >>> old.IDefineUnauthenticatedPrincipalDirective is new.IDefineUnauthenticatedPrincipalDirective
      True
      >>> old.IDefineUnauthenticatedGroupDirective is new.IDefineUnauthenticatedGroupDirective
      True
      >>> old.IDefineAuthenticatedGroupDirective is new.IDefineAuthenticatedGroupDirective
      True
      >>> old.IDefineEverybodyGroupDirective is new.IDefineEverybodyGroupDirective
      True

      >>> import zope.app.security.metaconfigure as old
      >>> import zope.principalregistry.metaconfigure as new

      >>> old.principal is new.principal
      True
      >>> old.unauthenticatedPrincipal is new.unauthenticatedPrincipal
      True
      >>> old.unauthenticatedGroup is new.unauthenticatedGroup
      True
      >>> old.authenticatedGroup is new.authenticatedGroup
      True
      >>> old.everybodyGroup is new.everybodyGroup
      True

    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))
