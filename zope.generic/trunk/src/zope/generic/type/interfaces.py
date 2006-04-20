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
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Object

from zope.generic.configuration import IConfigurationType
from zope.generic.directlyprovides import IProvides
from zope.generic.informationprovider import IInformationProvider
from zope.generic.keyface import IKeyface
from zope.generic.keyface import IKeyfaceType


__all__ = ['ITypeType', 'ITypeable', 'ITyped', 'IDirectlyTyped', 
           'ITypeInformation', 'IInitializer', 'IInitializationHandler', 
           'IInitializerConfiguration']



class ITypeType(IKeyfaceType):
    """An abstract interface marker marker type.

    An interface marked by this marker type will provide an typed information
    within the corresponding ITypeInformation registry.
    """



class ITypeable(Interface):
    """Assert ITyped by adaption or by implementation."""



class ITyped(ITypeable, IKeyface):
    """Provid an information within the."""

    keyface = Object(
        title=_('Key interface'),
        description=_('Key interface that references corresponding type informations.'),
        required=True,
        schema=ITypeType)



class IDirectlyTyped(ITyped, IProvides, IKeyface):
    """Directly provide the declared interface."""

    def __init__(__keyface__, *pos, **kws):
        """Directly provide the key interface during the __init__ call."""

    __keyface__ = Object(
        title=_('Key interface'),
        description=_('The declared key interface must be directly provided too.'),
        required=True,
        readonly=True,
        schema=ITypeType)



class ITypeInformation(IInformationProvider):
    """Provide information for the declared type interface."""



class IInitializer(Interface):
    """Initialize an object."""

    def __call__(*pos, **kws):
        """Invoke initialization handler declared by the initializer configuration."""



class IInitializationHandler(Interface):
    """Initialize an object."""

    def __call__(context, *pos, **kws):
        """Initialize the object referenced by self."""



class IInitializerConfiguration(Interface):
    """Provide initialization handler.

    At least a handler or an interface must be defined.

    If the interface is defined, **kws are stored as configuration defined by
    the interface.

    If the **kws does not satify the interface a KeyError is raised.
    """

    keyface = Object(
        title=_('Configuration interface'),
        description=_('Configuration interface defining the signature.'),
        required=False,
        schema=IConfigurationType)

    handler = Object(
        title=_('Initialization Handler'),
        description=_('Callable (context, *pos, **kws).'),
        required=False,
        schema=IInitializationHandler)

alsoProvides(IInitializerConfiguration, IConfigurationType)
