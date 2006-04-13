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
from zope.interface.interfaces import IInterface
from zope.schema import Bool
from zope.schema import Object
from zope.schema import Tuple

from zope.generic.component import IKeyInterface
from zope.generic.configuration import IConfigurationType
from zope.generic.information import IInformation
from zope.generic.information import IInformationRegistryType
from zope.generic.type import ITypeType



class IContextProxy(Interface):
    """Proxy the context of a component."""

    def __conform__(interface):
        """Might cache adapters."""

    def __getattr__(name):
        """Get an attribute of
        """
    def __setattr__(name, value):
        """Set an attribute of."""



class IOperation(IKeyInterface):
    """Proceed operation"""

    def __call__(context, *pos, **kws):
        """Proceed the operation on the given context.

        Public operation requires zero to n configuations.
        The configuration can be passed as *pos, **kws. If no arguments are
        passed the operation should lookup the declared configurations on the
        context.
        
        If pos we assume one configuration or dict in order to the declared order.
        If not pos we extact the kws as configuration data
        """



class IOperationInformation(IInformation):
    """Registration about an global operation."""

alsoProvides(IOperationInformation, IInformationRegistryType)



class IOperationType(IInterface):
    """Mark operation marker interface."""



class IPrivateOperation(Interface):
    """Mark private callables."""

alsoProvides(IPrivateOperation, IOperationType)



class IOperationConfiguration(Interface):
    """Tell the controller which handler should be invoked."""

    operation = Object(title=_('Operation'),
        description=_('Callable operation.'),
        required=False,
        schema=IOperation)

    input = Tuple(title=_('Input Configurations'),
        description=_('Tuple of configuration schema that will be respected.'),
        required=False,
        default=(),
        value_type=Object(schema=IConfigurationType))

    output = Tuple(title=_('Output Configurations'),
        description=_('Tuple of configuration schema that might be modified or created.'),
        required=False,
        default=(),
        value_type=Object(schema=IConfigurationType))



alsoProvides(IOperationConfiguration, IConfigurationType)
