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

from zope.annotation import IAnnotations
from zope.generic.face.api import acquireInformationProvider
from zope.generic.face.api import getConface
from zope.generic.face.api import getInformationProvider
from zope.generic.face.api import getInformationProvidersFor
from zope.generic.face.api import getKeyface
from zope.generic.face.api import queryInformationProvider
from zope.generic.face.api import toDottedName
from zope.generic.face.api import toInterface

from zope.generic.configuration import IConfigurations
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration.api import ConfigurationData

from zope.generic.informationprovider import *
from zope.generic.informationprovider.base import GlobalInformationProvider
from zope.generic.informationprovider.base import LocalInformationProvider
from zope.generic.informationprovider.base import UserDescription
from zope.generic.informationprovider.metaconfigure import ensureInformationProvider



def getInformation(context, informationkey):
    """Evaluate an information by a keyface (string or key keyface)."""
    if IConfigurationType.providedBy(informationkey):
        return informationkey(IConfigurations(context))

    else:
        return IAnnotations(context)[informationkey]



def queryInformation(context, informationkey, default=None):
    """Evaluate an information by a keyface (string or key interface)."""
    try:
        return getInformation(context, informationkey)

    except:
        return default



def provideInformation(context, informationkey, information):
    """Set an information to a context using a keyface (string or key interface)."""

    if IConfigurationType.providedBy(informationkey):
        if type(information) is dict:
            information = ConfigurationData(informationkey, information)
    
        IConfigurations(context)[informationkey] = information

    else:
        IAnnotations(context)[informationkey] = information



def deleteInformation(context, informationkey):
    """Delete an information of a context using a keyface (string or key interface)."""

    if IConfigurationType.providedBy(informationkey):
        del IConfigurations(context)[informationkey]
    
    else:
        del IAnnotations(context)[informationkey]
