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
"""Skin Preferences Realization

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.publisher.interfaces.browser import ISkin
from zope.app.component.interfaces import ISite
from zope.app.preference.interfaces import IUserPreferences
from zope.app.publisher.browser import applySkin as applySkinOnRequest

def applySkin(event):
    # We only want to look for a new skin to set, if we entered a new site.
    if not ISite.providedBy(event.object):
        return
    
    # Find the user's skin
    prefs = IUserPreferences(event.object)
    skin = prefs.zmi.skin.skin

    # Only change the skin, if request does not have this skin
    if not skin or skin.providedBy(event.request):
        return

    # Remove the old skin and apply new one
    applySkinOnRequest(event.request, skin)
