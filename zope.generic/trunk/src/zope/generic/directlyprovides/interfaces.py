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

from zope.interface import Attribute
from zope.interface import Interface

from zope.app.event.interfaces import IObjectEvent

from zope.app.i18n import ZopeMessageFactory as _



class IProvides(Interface):
    """Prependes important interfaces within the directly provides mechanism."""

    __provides__ = Attribute(_('Provides'),
        _('Return directly provided interfaces respecting a partial order of ' +
          'important interfaces that should be prepended any time.')
        )



class IDirectlyProvidesModifiedEvent(IObjectEvent):
    """Reference an object where the directly provided interfaces were modified."""



class IObjectModifiedEventDispatchingProvides(IProvides):
    """Marked objects will be notify an additional ObjectModifiedEvent.

    This interface is used for subscriber-based event dispatching.
    """
