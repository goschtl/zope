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

from zope.generic.information.api import getInformation
from zope.generic.configuration.api import getConfigurationData

from zope.generic.operation import IOperationInformation
from zope.generic.operation import IOperationConfiguration



def getOperationInformation(object):
    """Evaluate an operation information from an object."""
    return getInformation(object, IOperationInformation)



def queryOperationInformation(object, default=None):
    """Evaluate an operation information from an object or return default."""
    try:
        return getOperationInformation(object)

    except:
        return default



def getOperationConfiguration(object):
    """Evaluate an operation configuration."""
    
    return getConfigurationData(getOperationInformation(object), IOperationConfiguration)



def queryOperationConfiguration(object, default=None):
    """Evaluate an operation configuration or default."""
    try:
        return getOperationConfiguration(object)

    except:
        return default



def queryOperation(interface, default=None):
    """Return the operation of operation marker."""

    try:
        return getOperationConfiguration(interface).operation

    except:
        return default



def queryOperationInput(interface, default=None):
    """Return the input paramters of an operation as tuple of configuration interfaces."""

    try:
        return getOperationConfiguration(interface).input

    except:
        return default



def queryOperationOutput(interface, default=None):
    """Return the ouput paramters of an operation as tuple of configuration interfaces."""

    try:
        return getOperationConfiguration(interface).output

    except:
        return default
