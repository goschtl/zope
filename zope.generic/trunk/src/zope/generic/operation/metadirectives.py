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

from zope.generic.component import IConfigurationType
from zope.generic.component.metadirectives import IBaseInformationDirective



class IOperationDirective(IBaseInformationDirective):
    """Register a public operation.

    The operation will be registered as interface utility typed by IOperationType.
    """

    operations = Tokens(
        title=_('Operation or IOperationType'),
        description=_('Global operation or callable(context) or IOperationType interface.'),
        required=False,
        value_type=GlobalObject()
        )

    input = Tokens(title=_('Input Configurations'),
        description=_('Tuple of configuration schema that will be respected.'),
        required=False,
        value_type=GlobalInterface())

    output = Tokens(title=_('Output Configurations'),
        description=_('Tuple of configuration schema that might be modified or created.'),
        required=False,
        value_type=GlobalInterface())
        