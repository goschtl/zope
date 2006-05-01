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
from zope.schema import Object
from zope.schema import Tuple

from zope.generic.configuration import IConfiguration
from zope.generic.face import IConfaceType
from zope.generic.face import IFace
from zope.generic.face import IKeyfaceType



class IContextProxy(Interface):
    """Proxy the context of a component."""

    def __conform__(keyface):
        """Might cache adapters."""

    def __getattr__(name):
        """Get an attribute of
        """
    def __setattr__(name, value):
        """Set an attribute of."""



class IOperation(IFace):
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



class IOperationContext(Interface):
    """Registration about an global operation."""

alsoProvides(IOperationContext, IConfaceType)



class IPrivateOperation(Interface):
    """Marker private, undefined callables."""

alsoProvides(IPrivateOperation, IKeyfaceType)



class IOperationConfiguration(Interface):
    """Tell the controller which handler should be invoked."""

    operation = Object(title=_('Operation'),
        description=_('Callable operation.'),
        required=False,
        schema=IOperation)

    input = Tuple(title=_('Input Declaration'),
        description=_('A configuration interface declaring the input parameters.'),
        required=False,
        default=(),
        value_type=Object(schema=IConfiguration))

    output = Tuple(title=_('Output Declaration'),
        description=_('An interface interface declaring the output parameters.'),
        required=False,
        default=(),
        value_type=Object(schema=IInterface))



alsoProvides(IOperationConfiguration, IConfiguration)
