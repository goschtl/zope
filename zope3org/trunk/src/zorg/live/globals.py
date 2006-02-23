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

$Id: globals.py 39651 2005-10-26 18:36:17Z oestermeier $
"""

from zope.app import zapi

from zope.component import ComponentLookupError
from zope.app.security.interfaces import PrincipalLookupError

from zope.security.management import queryInteraction
from zope.publisher.interfaces import IRequest

defaultRequest = None

def getRequest() :
    global defaultRequest
    interaction = queryInteraction()
    if interaction is not None:
        for participation in interaction.participations:
            if IRequest.providedBy(participation) :
                return participation
    return defaultRequest
    

def getFullName(principal_id) :
    """ Returns the full name or title of a principal that can be used
        for better display.
        
        Returns the id if the full name cannot be found.
    """
    try :
        return zapi.principals().getPrincipal(principal_id).title
    except (PrincipalLookupError, AttributeError, ComponentLookupError) :
        return principal_id
