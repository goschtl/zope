##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id: $
"""

import zope.component
import zope.app.testing.placelesssetup

from zopeorgwikiimporter import ImporterForContainer

class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)
        
        # zope.app.annotations
        from zope.app.annotation.interfaces import IAnnotations
        from zope.app.annotation.attribute import AttributeAnnotations
        from zope.app.file.interfaces import IFile

        zope.component.provideAdapter(AttributeAnnotations,
            [IFile], IAnnotations)

        # dublin core annotations
        from zope.app.dublincore.interfaces import IWriteZopeDublinCore
        from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter

        zope.component.provideAdapter(ZDCAnnotatableAdapter,
            [IFile], IWriteZopeDublinCore)

        # importer for container
        zope.component.provideAdapter(ImporterForContainer)

    def tearDown(self, test=None):
        super(PlacelessSetup, self).tearDown()

placelesssetup = PlacelessSetup()