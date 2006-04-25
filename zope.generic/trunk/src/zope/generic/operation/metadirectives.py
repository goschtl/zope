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
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import Tokens
from zope.interface import Interface

from zope.generic.configuration import IConfigurationType
from zope.generic.informationprovider.metadirectives import IBaseInformationProviderDirective



class IBaseOperationDirective(Interface):
    """Register an operation."""

    operations = Tokens(
        title=_('Callable, Operation or IOperationType'),
        description=_('Callable(context, *pos, **kws), global operation ' +
                      'or IOperationType key interface.'),
        required=False,
        value_type=GlobalObject()
        )

    input = GlobalInterface(title=_('Input Declaration'),
        description=_('Configuration schema describing the input arguments.'),
        required=False)



class IOperationDirective(IBaseInformationProviderDirective, IBaseOperationDirective):
    """Register a public operation.

    The operation will be registered as information provider utility providing
    IOperationInformation.

    The operation key interface will be registered as interface utility typed as
    IOperationType too.
    """

    output = GlobalInterface(title=_('Output Declaration'),
        description=_('Configuration schema or interface describing the input arguments.'),
        required=False)