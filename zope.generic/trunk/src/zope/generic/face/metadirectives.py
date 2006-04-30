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
from zope.interface import Interface


class IKeyfaceDirective(Interface):
    """Key interface registration directive."""

    keyface = GlobalInterface(
        title=_('Key Interface'),
        description=_('Interface that represents an information key.'),
        required=False
        )



class IConfaceDirective(Interface):
    """Context interface registration directive."""

    conface = GlobalInterface(
        title=_('Context Interface'),
        description=_('Interface that represents an information context.'),
        required=False
        )



class IFaceDirective(IKeyfaceDirective, IConfaceDirective):
    """Key or context interface registration directive."""

    type = GlobalInterface(
        title=_('Type'),
        description=_('Type a key or contex interface by a regular type or type '
                      'an key interface and interfac providing IConfaceType.'),
        required=False
        )
