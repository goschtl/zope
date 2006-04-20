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

from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import alsoProvides

from zope.generic.keyface import IKeyfaceType
from zope.generic.keyface import IKeyfaceDescription



###############################################################################
#
# base configurations related interfaces 
#
###############################################################################


class IInformationProviderType(IKeyfaceType):
    """Mark information interface as information type."""



class IInformationProvider(IKeyfaceDescription):
    """Provide information about a dedicated key interfaces.
    
    A configuration related to the key interface can be stored within the
    provider's configurations.
    
    Dedicated information providers has to extend this interface.
    """



class IInformationProviderInformation(IInformationProvider):
    """Provide information about information providers."""



alsoProvides(IInformationProviderInformation, IInformationProviderType)

