##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Object that takes care of annotating the dublin core creator field.

$Id: creatorannotator.py,v 1.3 2003/05/21 17:26:38 sidnei Exp $
"""
__metaclass__ = type

from zope.component import queryAdapter
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.event import ISubscriber
from zope.security.management import getSecurityManager

class CreatorAnnotatorClass:
    """Update Dublin-Core creator property
    """
    __implements__ = ISubscriber

    def notify(self, event):
        dc = queryAdapter(event.object, IZopeDublinCore)
        if dc is None:
            return

        # Try to find a principal for that one. If there
        # is no principal then we don't touch the list
        # of creators.
        principal = getSecurityManager().getPrincipal()
        if principal is None:
            return
        principalid = principal.getId()
        if not principalid in dc.creators:
            dc.creators = dc.creators + (principalid, )

CreatorAnnotator = CreatorAnnotatorClass()
