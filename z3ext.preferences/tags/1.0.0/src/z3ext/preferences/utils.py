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
"""

$Id$
"""
from zope import interface
from zope.security.interfaces import IPrincipal, IGroup, IMemberAwareGroup


def isUser(group):
    principal = group.__principal__
    return IPrincipal.providedBy(principal) and not IGroup.providedBy(principal)


def isGroup(group):
    return IGroup.providedBy(group.__principal__)


def isMemberAwareGroup(group):
    return IMemberAwareGroup.providedBy(group.__principal__)
