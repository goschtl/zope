##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Sharing utility functions

$Id$
"""
from zope.location.interfaces import ISublocations

from zc.sharing.interfaces import ISharing
from zc.sharing.sharing import sharingMask

def shareAll(ob, principal_id):
    sharing = ISharing(ob)
    mask = sharingMask(ob)
    sharing.setBinaryPrivileges(principal_id, mask)

def applyToSubobjects(settings, ob, seen=None, clobber=False):
    """Apply the given sharing settings to all subobjects of `ob`
    
    clobber - a boolean, if true no sharing bits will be left enabled for an
        object unless they exist in that objects sharing mask
    """
    if seen is None:
        seen = {}

    obid = id(ob)
    if obid in seen:
        return
    seen[obid] = ob

    sharing = ISharing(ob, None)
    if sharing is not None:
        mask = sharingMask(ob)
        for principal_id, setting in settings:
            if not clobber:
                value = sharing.getBinaryPrivileges(principal_id)
                # unmasked_value represents all of the bits of value that fall
                # outside of the mask
                unmasked_value = (value & mask) ^ value
                setting |= unmasked_value

            sharing.setBinaryPrivileges(principal_id, setting)

    subs = ISublocations(ob, None)
    if subs is not None:
        for sub in subs.sublocations():
            applyToSubobjects(settings, sub, seen, clobber)
