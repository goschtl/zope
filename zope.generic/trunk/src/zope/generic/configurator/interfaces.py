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

from zope.app.annotation import IAnnotations
from zope.interface import Interface
from zope.schema import Object

from zope.generic.configuration import IConfiguraitons



class IConfigurator(Interface):
    """Configure an component."""

    def configure(component, *pos, **kws):
        """Configure the component."""

    configurations = Object(
        title=_('Configurations'),
        description=_('The configurations of the component.'),
        required=False,
        readonly=True,
        schema=IConfigurations)

    annotations = Object(
        title=_('Annotations'),
        description=_('The annotations of the component.'),
        required=False,
        readonly=True,
        schema=IAnnotations)




class IInitializer(IConfigurator):
    """Initialize an object."""



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

    interface = Object(
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
