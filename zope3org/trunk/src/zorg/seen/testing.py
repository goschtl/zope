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

$Id: testing.py 39651 2005-10-26 18:36:17Z oestermeier $
"""

import zope.component

import zope.app.testing.placelesssetup



class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)
        
        # zope.app.annotations
        from zope.app.annotation.interfaces import IAnnotations
        from zope.app.annotation.interfaces import IAttributeAnnotatable
        from zope.app.annotation.attribute import AttributeAnnotations

        zope.component.provideAdapter(AttributeAnnotations,
            [IAttributeAnnotatable], IAnnotations)

        # seen.seen adapter
        from zorg.seen.seen import SeenForAnnotableObjects
        from zorg.seen.interfaces import ISeen
        zope.component.provideAdapter(SeenForAnnotableObjects, 
                                                    provides=ISeen)

    def tearDown(self, test=None):
        super(PlacelessSetup, self).tearDown()

placelesssetup = PlacelessSetup()
