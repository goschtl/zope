##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""The basic bundle.

$Id: __init__.py,v 1.3 2004/04/17 15:13:01 jim Exp $
"""
from zope.app.container.btree import BTreeContainer
from interfaces import IBundle
from zope.app.registration.registration import RegisterableContainer
from zope.interface import implements


class Bundle(RegisterableContainer, BTreeContainer):
    implements(IBundle)
