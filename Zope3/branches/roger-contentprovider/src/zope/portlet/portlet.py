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
"""Portlet implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface
#from zope.viewlet.viewlet import ViewletManager
from zope.portlet.interfaces import IPortletManager


#class DefaultPortletManager(ViewletManager):
class DefaultPortletManager(object):
    """Default portlet manager."""

    zope.interface.implements(IPortletManager)

