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
""" Register security related configuration directives.

$Id: metaConfigure.py,v 1.3 2002/06/20 15:54:59 jim Exp $
"""

from Zope.Configuration.Action import Action
from Zope.Security.SecurityManager import setSecurityPolicy

def securityPolicy(_context, name):
    policy = _context.resolve(name)
    if callable(policy):
        policy = policy()
    return [
        Action(
            discriminator = 'defaultPolicy',
            callable = setSecurityPolicy,
            args = (policy,),
            )
        ]


