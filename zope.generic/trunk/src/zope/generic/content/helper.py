##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.generic.face.api import getKeyface
from zope.generic.face.api import getInformationProvider
from zope.generic.informationprovider.api import queryInformation

from zope.generic.face import IUndefinedContext




def getTypeInformation(object, conface=IUndefinedContext):
    return getInformationProvider(getKeyface(object), conface)



def queryTypeInformation(object, default=None):
    """Lookup an type information of any object."""

    try:
        return getTypeInformation(object)

    except:
        return default



def queryObjectConfiguration(object, configuration, default=None):   
    return queryInformation(object, configuration, default)



def queryTypeConfiguration(object, configuration, default=None):
    info = queryTypeInformation(object)
    return queryInformation(info, configuration, default)



def acquireTypeConfiguration(object, configuration, default=None):
    try:
        keyface = getKeyface(object, default)

    except:
        return default



def acquireObjectConfiguration(object, configuration, default=None):
    # first try to evaluate object configuration data
    data = queryObjectConfiguration(object, configuration, default)

    if data is not default:
        return data
    
    # return type configuration data
    else:
        return queryTypeConfiguration(object, configuration, default)
