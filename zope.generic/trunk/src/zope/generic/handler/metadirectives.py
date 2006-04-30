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

from zope.generic.face.metadirectives import IKeyfaceDirective
from zope.generic.operation.metadirectives import IBaseOperationDirective



class IBaseHandlerDirective(Interface):
    """Base handler directive."""

    event = GlobalInterface(
        title=_('Event'),
        description=_('The event to be listened.'),
        required=True
        )


class IHandlerDirective(IKeyfaceDirective, IBaseHandlerDirective, IBaseOperationDirective):
    """Provide trusted locatable handler that invoke operations."""
