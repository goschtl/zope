##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" interfaces relateds to view preference groups

$Id$
"""
from zope import interface


class IPreferences(interface.Interface):
    """ preferences """


class IPreferenceGroupView(interface.Interface):
    """ group view """

    def isAvailable():
        """ is this view available """

    def render():
        """ render view """


class IPreferenceGroupPreview(IPreferenceGroupView):
    """ group preview """


class IDefaultPreferenceGroupView(interface.Interface):
    """ default preference view """
