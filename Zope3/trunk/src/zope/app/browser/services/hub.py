##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Define view component for object hub.

$Id: hub.py,v 1.4 2003/08/07 17:41:03 srichter Exp $
"""
from zope.app.interfaces.services.hub import IObjectHub

class Control:
    __used_for__ = IObjectHub

    # XXX: Another dead chicken. Guys, this view could do soo much, like aehm,
    # display the cataloged objects with a nice filter function?
