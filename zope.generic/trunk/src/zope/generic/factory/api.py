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

from zope.generic.informationprovider.api import getNextInformationProvider
from zope.generic.informationprovider.api import queryInformation
from zope.generic.face.api import toDottedName
from zope.generic.operation import IOperationConfiguration

from zope.generic.factory import *




def createObject(keyface, *pos, **kws):
    """Create an instance of a logical type using the type marker."""
    return component.createObject(toDottedName(keyface), *pos, **kws)



def createParameter(keyface):
    """Evaluate initializer parameters."""
    provider = getNextInformationProvider(keyface, IFactory)
    config = queryInformation(provider, IOperationConfiguration)
    if config:
        return config.input
    
    else:
        return None
