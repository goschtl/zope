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

$Id: bundle.py,v 1.1 2003/08/08 21:56:21 fdrake Exp $
"""

from zope.app.interfaces.container import IContainer
from zope.app.interfaces.services.registration \
     import IRegistrationManagerContainer

class IBundle(IContainer, IRegistrationManagerContainer):
    """Component and component registration containers."""
