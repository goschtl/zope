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
from zope.generic.configuration.api import queryConfigurationData

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



def queryOperationConfiguration(object, default=None):
    """Evaluate an operation configuration."""

    info = queryOperationInformation(object, default)
    if info is default:
        return default
    
    return queryConfigurationData(info, IOperationConfiguration)
