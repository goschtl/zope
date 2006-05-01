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

from zope.generic.face import IConfaceType
from zope.generic.face.metadirectives import IKeyfaceDirective



class IBaseInformationProviderDirective(IKeyfaceDirective):
    """Base information provider attributes."""

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
    """Directive to register an information to information provider."""

    conface = GlobalInterface(
        title=_('Context Interface'),
        description=_('The context interface provided by the information provider.'),
        required=True,
        constraint=lambda v: IConfaceType.providedBy(v)
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
        title=_('Annotation key'),
        description=_('Annotation key referencing an annotation.'),
        required=False
        )

    annotation = GlobalObject(
        title=_('Annotation'),
        description=_('Annotation component expected undert the key.'),
        required=False
        )
