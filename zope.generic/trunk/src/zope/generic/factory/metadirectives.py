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
from zope.configuration.fields import Bool
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

from zope.generic.informationprovider.metadirectives import IBaseInformationProviderDirective
from zope.generic.operation.metadirectives import IBaseOperationDirective


class IBaseFactoryDirective(Interface):
    """Declare a factory."""

    class_ = GlobalObject(
        title=_('Class'),
        description=_('Generic class implementation.'),
        required=True
        )

    providesKeyface = Bool(
        title=_('Provides Keyface'),
        description=_('If the class does not implement the key interface ' +
                      'directly provide it to the instances ' +
                      'before initalization.'),
        required=False,
        default=False
        )

    storeInput = Bool(
        title=_('Store Input'),
        description=_('Store input configuration within the objects configurations.'),
        required=False,
        default=False
        )

    notifyCreated = Bool(
        title=_('Notify created'),
        description=_('Notify an object created event after the initialization is fullfilled.'),
        required=False,
        default=False
        )


class IFactoryDirective(IBaseInformationProviderDirective, IBaseFactoryDirective, IBaseOperationDirective):
    """Register a public factory.

    The factory will be registered as information provider utility providing
    IFactoryInformation.
    """



