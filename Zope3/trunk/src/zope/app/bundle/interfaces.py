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
"""Interfaces for bundles.

$Id: interfaces.py,v 1.1 2004/03/10 13:11:13 srichter Exp $
"""
from zope.app.container.interfaces import IContainer
from zope.app.interfaces.services.registration \
     import IRegistrationManagerContainer

class IBundle(IContainer, IRegistrationManagerContainer):
    """Component and component registration containers."""
