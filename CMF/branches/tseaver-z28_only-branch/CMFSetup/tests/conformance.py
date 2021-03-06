##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Base classes for testing interface conformance.

Derived testcase classes should define '_getTargetClass()', which must
return the class being tested for conformance.

$Id$
"""

class ConformsToISetupContext:

    def test_ISetupContext_conformance( self ):

        from Products.CMFSetup.interfaces import ISetupContext
        from Interface.Verify import verifyClass

        verifyClass( ISetupContext, self._getTargetClass() )

class ConformsToIImportContext:

    def test_IImportContext_conformance( self ):

        from Products.CMFSetup.interfaces import IImportContext
        from Interface.Verify import verifyClass

        verifyClass( IImportContext, self._getTargetClass() )

class ConformsToIExportContext:

    def test_IExportContext_conformance( self ):

        from Products.CMFSetup.interfaces import IExportContext
        from Interface.Verify import verifyClass

        verifyClass( IExportContext, self._getTargetClass() )

class ConformsToIStepRegistry:

    def test_IStepRegistry_conformance( self ):

        from Products.CMFSetup.interfaces import IStepRegistry
        from Interface.Verify import verifyClass

        verifyClass( IStepRegistry, self._getTargetClass() )

class ConformsToIImportStepRegistry:

    def test_IImportStepRegistry_conformance( self ):

        from Products.CMFSetup.interfaces import IImportStepRegistry
        from Interface.Verify import verifyClass

        verifyClass( IImportStepRegistry, self._getTargetClass() )

class ConformsToIExportStepRegistry:

    def test_IExportStepRegistry_conformance( self ):

        from Products.CMFSetup.interfaces import IExportStepRegistry
        from Interface.Verify import verifyClass

        verifyClass( IExportStepRegistry, self._getTargetClass() )

class ConformsToIToolsetRegistry:

    def test_IToolsetRegistry_conformance( self ):

        from Products.CMFSetup.interfaces import IToolsetRegistry
        from Interface.Verify import verifyClass

        verifyClass( IToolsetRegistry, self._getTargetClass() )

class ConformsToIProfileRegistry:

    def test_IProfileRegistry_conformance( self ):

        from Products.CMFSetup.interfaces import IProfileRegistry
        from Interface.Verify import verifyClass

        verifyClass( IProfileRegistry, self._getTargetClass() )

class ConformsToISetupTool:

    def test_ISetupTool_conformance( self ):

        from Products.CMFSetup.interfaces import ISetupTool
        from Interface.Verify import verifyClass

        verifyClass( ISetupTool, self._getTargetClass() )
