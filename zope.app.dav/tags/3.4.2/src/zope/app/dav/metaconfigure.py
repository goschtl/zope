##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Configuration handlers for 'dav' namespace.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component.zcml import utility
from zope.interface import directlyProvides
from zope.app.dav.interfaces import IDAVNamespace

def interface(_context, for_, interface):
    directlyProvides(interface, IDAVNamespace)
    utility(_context, IDAVNamespace, interface, name=for_)
