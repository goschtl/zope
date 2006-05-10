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
from zope.configuration.fields import GlobalInterface
from zope.interface import Interface


class IConfigurationDirective(Interface):
    """Type a configuration key interface."""

    keyface = GlobalInterface(
        title=_('Key Interface'),
        description=_('Type a key interface to a configuration or nested '
                      'configuration type.'),
        required=True,
        )

    nested = Bool(
        title=_('Nested'),
        description=_('Turn on nested configuration support.'),
        required=False,
        )
