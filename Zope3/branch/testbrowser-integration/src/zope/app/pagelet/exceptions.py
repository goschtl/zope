##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pagelet exceptions

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component import ComponentLookupError

from zope.app.i18n import ZopeMessageIDFactory as _




class PageletSlotInterfaceLookupError(ComponentLookupError):
    """IPageletSlot slot interface not found."""

PageletError_slot_interface_not_found = _(
    u'Pagelet slot interface not found.')


class PageletSlotInterfaceNotProvidedException(Exception):
    """IPageletSlot interface not provided."""

PageletError_slot_interface_not_provided = _(
    u'IPageletSlot interface not provided.')
