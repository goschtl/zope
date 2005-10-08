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
"""Portlet state handler implementation

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface

from zope.portlet import interfaces



class PreferenceStateHandler(object):
    """State handler based on preferences."""

    implements(interfaces.IStateHandler)

    def __init__(self, context):
        self.context = context
        self.preferences = None

    def setState(self, name, value):
        """xxx"""
        # self.preferences.portletmanager.%s.state = %s % (portletname, name)

