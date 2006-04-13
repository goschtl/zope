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

from zope import component

from zope.generic.component.api import toDottedName
from zope.generic.component.api import queryInformation
from zope.generic.component.api import queryInformationProvider

from zope.generic.type import IInitializerConfiguration
from zope.generic.type import ITypeInformation
from zope.generic.type import ITyped
from zope.generic.type import ITypeType



def createObject(interface, *pos, **kws):
    """Create an instance of a logical type using the type marker."""
    return component.createObject(toDottedName(interface), *pos, **kws)


def createParameter(interface):
    config = queryTypeConfiguration(interface, IInitializerConfiguration)
    if config:
        return config.interface
    
    else:
        return None



def getType(object):
    """Evaluate relevant type marker interface of an object."""

    if ITypeType.providedBy(object):
        interface = object

    elif ITyped.providedBy(object):
        interface = object.interface

    else:
        interface = ITyped(object).interface

    return interface



def queryType(object, default=None):
    try:
        return getType(object)
    
    except:
        return default



def getTypeInformation(object):
    return queryInformationProvider(getType(object), ITypeInformation)



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
        interface = getType(object, default)

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

