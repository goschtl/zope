##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Test Setup.

$Id$
"""
import zope.component
import zope.testing.doctest
from zope.app.testing import placelesssetup, setup

from keas.googlemap import geocode

def setUpGoogleMap():
    setup.setUpAnnotations()
    zope.component.provideAdapter(geocode.getGeocodeAnnotation)
    zope.component.provideAdapter(geocode.getGeocodeFromQuery)
