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



class IKeyFaceDirective(Interface):
    """Base information attributes."""

    keyface = GlobalInterface(
        title=_('Key Interface'),
        description=_('Interface that represents an information key.'),
        required=True
        )

    type = GlobalInterface(
        title=_('Key Interface Type'),
        description=_('Type a key interface by an interface derived from ' +
                      'IKeyfaceType. If no type provided the interface will ' +
                      'marked by IKeyfaceType.'),
        required=False
        )
