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
""" Register Application Control configuration directives.

$Id: metaConfigure.py,v 1.2 2002/06/10 23:27:51 jim Exp $
"""

from ApplicationControl import ApplicationController
from Zope.Configuration.Action import Action


def registerView(_context, name, title):
    return [
        Action(
            discriminator = ('application-control:registerView', name),
            callable = ApplicationController.registerView,
            args = (name, title),
            )
        ]

