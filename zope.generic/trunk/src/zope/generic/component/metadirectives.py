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
from zope.configuration.fields import MessageID
from zope.interface import Interface

from zope.generic.component import IInformationProvider



class IBaseInformationProviderDirective(Interface):
    """Base information attributes."""

    keyface = GlobalInterface(
        title=_('Interface'),
        description=_('Interface that represents an information.'),
        required=True
        )

    label = MessageID(
        title=_('Label'),
        description=_('Label of the information.'),
        required=False
        )

    hint = MessageID(
        title=_('Hint'),
        description=_('Hint of the informtion.'),
        required=False
        )



class IConfigurationDirective(IBaseInformationProviderDirective):
    """Declare configuration schema.

    Register configuration schema as interface utility typed by
    IConfigurationType within the configuration registry utility.    
    """



class IInformationProviderDirective(IBaseInformationProviderDirective):
    """Directive to register an information to corresponding information
    registry."""

    registry = GlobalInterface(
        title=_('Information Registry Key'),
        description=_('A registry key is a dedicated interface which should extend' +
                      'IInformationProvider.'),
        required=True,
        constraint=lambda v: v.extends(IInformationProvider)
        )



class IConfigurationSubdirective(Interface):
    """Declare a certain configuration of a type."""

    keyface = GlobalInterface(
        title=_('Interface'),
        description=_('Interface referencing a configuraiton.'),
        required=True
        )

    data = GlobalObject(
        title=_('Data'),
        description=_('Configuration data component providing the configuraiton interface.'),
        required=True
        )

