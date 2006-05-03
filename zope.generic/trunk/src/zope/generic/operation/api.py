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
from zope.generic.face import IUndefinedContext
from zope.generic.informationprovider.api import getInformationProvider
from zope.generic.informationprovider.api import getInformation

from zope.generic.operation.interfaces import *
from zope.generic.operation.metaconfigure import assertOperation



def getOperationConfiguration(object, conface=IUndefinedContext):
    """Evaluate an operation configuration."""
    
    return getInformation(IOperationConfiguration, getInformationProvider(object, conface))



def getOperation(keyface, conface=IUndefinedContext):
    """Return the operation of operation marker."""

    return getOperationConfiguration(keyface, conface).operation




def inputParameter(object, conface=IUndefinedContext):
    """Return the input paramters of an operation as tuple of configuration keyfaces."""

    return getOperationConfiguration(object, conface).input




def outputParameter(object, conface=IUndefinedContext):
    """Return the ouput paramters of an operation as tuple of configuration keyfaces."""

    return getOperationConfiguration(object, conface).output
