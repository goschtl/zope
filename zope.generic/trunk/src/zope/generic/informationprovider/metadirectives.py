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
from zope.schema import DottedName

from zope.generic.informationprovider import IInformationProvider



class IBaseInformationProviderDirective(Interface):
    """Base information provider attributes."""

    keyface = GlobalInterface(
        title=_('Key Interface'),
        description=_('Key interface that is refered by the information.'),
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



class IInformationSubdirective(Interface):
    """Declare a certain information of an information provider."""

    keyface = GlobalInterface(
        title=_('Interface'),
        description=_('Interface referencing a configuraiton.'),
        required=False
        )

    configuration = GlobalObject(
        title=_('Configuration'),
        description=_('Configuration component providing the key interface.'),
        required=False
        )

    key = DottedName(
        title=_('Interface'),
        description=_('Interface referencing a configuraiton.'),
        required=False
        )

    annotation = GlobalObject(
        title=_('Annotation'),
        description=_('Annotation component expected undert the key.'),
        required=False
        )
