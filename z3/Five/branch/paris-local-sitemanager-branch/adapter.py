##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Generic Components ZCML Handlers

$Id: metaconfigure.py 9769 2005-03-14 17:37:00Z dreamcatcher $
"""
from Acquisition import aq_inner, aq_parent
from zope.app.site.interfaces import ISite
from zope.component.exceptions import ComponentLookupError

def serviceServiceAdapter(ob):
    """An adapter * -> IServiceService.

    This is registered in place of the one in Zope 3 so that we lookup
    using acquisition instead of ILocation.
    """
    current = ob
    while True:
        if ISite.providedBy(current):
            return current.getSiteManager()
        current = aq_parent(aq_inner(current))
        if current is None:
            raise ComponentLookupError("Could not adapt %r to"
                                       " IServiceService" % (ob, ))

