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

$Id: metaConfigure.py,v 1.3 2002/12/20 19:45:44 jim Exp $
"""

from ApplicationControl import applicationController
from Zope.Configuration.Action import Action


def registerView(_context, name, title):
    return [
        Action(
            discriminator = ('application-control:registerView', name),
            callable = applicationController.registerView,
            args = (name, title),
            )
        ]

