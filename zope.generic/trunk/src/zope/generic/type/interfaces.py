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

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import Interface
from zope.schema import Object

from zope.generic.configuration.api import IAttributeConfigurable
from zope.generic.informationprovider import IInformationProvider
from zope.generic.keyface import IKeyface
from zope.generic.keyface import IKeyfaceType
from zope.generic.keyface import IProvidesAttributeKeyfaced


__all__ = ['ITypeType', 'ITypeable', 'ITyped', 'IGenericTyped', 
           'ITypeInformation']



class ITypeType(IKeyfaceType):
    """An abstract interface marker marker type.

    An interface marked by this marker type will provide an typed information
    within the corresponding ITypeInformation registry.
    """



class ITypeable(Interface):
    """Assert ITyped by adaption or by implementation."""



class ITyped(ITypeable, IKeyface):
    """Provide the key interface."""

    keyface = Object(
        title=_('Key interface'),
        description=_('Key interface that references corresponding type informations.'),
        required=True,
        schema=ITypeType)



class IGenericTyped(ITyped, IProvidesAttributeKeyfaced, IAttributeConfigurable, IAttributeAnnotatable):
    """Directly provide the declared key interface interface."""



class ITypeInformation(IInformationProvider):
    """Provide information for the declared type interface."""

