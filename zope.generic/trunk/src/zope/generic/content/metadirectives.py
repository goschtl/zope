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

from zope.generic.adapter.metadirectives import IOthersAdapterDirective
from zope.generic.factory.metadirectives import IBaseFactoryDirective
from zope.generic.informationprovider.metadirectives import IBaseInformationProviderDirective
from zope.generic.handler.metadirectives import IBaseHandlerDirective
from zope.generic.operation.metadirectives import IBaseOperationDirective

    

class ITypeDirective(IBaseInformationProviderDirective):
    """Declare attriubtes of the type directive.

    Register an type information and a type factory.
    """



class IFactorySubdirective(IBaseFactoryDirective, IBaseOperationDirective):
    """Provide an factory for the type."""

    providesFace = Bool(
        title=_('Provides Face'),
        description=_('If the class does not implement the key interface '
                      'directly provide it to the instances '
                      'before initalization.'),
        required=False,
        default=True
        )


class IAdapterSubdirective(IOthersAdapterDirective):
    """Provide an adapter for the key interface."""

    acquire = Bool(
        title=_('Acquire Type Information'),
        description=_('If selected the type information are invoked.'),
        required=False,
        default=False
        )

class IHandlerSubdirective(IBaseHandlerDirective, IBaseOperationDirective):
    """Provide object event handler for the keyface."""
