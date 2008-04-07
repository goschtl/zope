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
""" custom IBreadcrumb implementation for IConfiglet

$Id$
"""
from zope import component, interface
from z3c.breadcrumb.browser import GenericBreadcrumb

from i18n import _
from interfaces import IPrincipalsManagement


class ManagementBreadcrumb(GenericBreadcrumb):
    component.adapts(IPrincipalsManagement, interface.Interface)

    name = _('Principals')
