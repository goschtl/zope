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

# usage see README.txt
from zope.generic.informationprovider.api import getInformationProvider
from zope.generic.informationprovider.api import getInformation

from zope.generic.operation.interfaces import *
from zope.generic.operation.metaconfigure import assertOperation
from zope.generic.operation.metaconfigure import provideOperationConfiguration



def getOperationInformation(object):
    """Evaluate an operation information from an object."""
    return getInformationProvider(object, IOperationInformation)



def queryOperationInformation(object, default=None):
    """Evaluate an operation information from an object or return default."""
    try:
        return getOperationInformation(object)

    except:
        return default



def getOperationConfiguration(object):
    """Evaluate an operation configuration."""
    
    return getInformation(getOperationInformation(object), IOperationConfiguration)



def queryOperationConfiguration(object, default=None):
    """Evaluate an operation configuration or default."""
    try:
        return getOperationConfiguration(object)

    except:
        return default



def getOperation(keyface, default=None):
    """Return the operation of operation marker."""

    return getOperationConfiguration(keyface).operation




def inputParameter(object, default=None):
    """Return the input paramters of an operation as tuple of configuration keyfaces."""

    return getOperationConfiguration(object).input




def outputParameter(object, default=None):
    """Return the ouput paramters of an operation as tuple of configuration keyfaces."""

    return getOperationConfiguration(object).output
