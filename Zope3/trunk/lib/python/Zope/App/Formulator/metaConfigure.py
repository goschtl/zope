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
"""

$Id: metaConfigure.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

from Zope.Configuration.Action import Action
from FieldRegistry import registerField
from ValidatorRegistry import registerValidator

def field(_context, name, field):
    """
    Note that most applications return an actual Action at this point;
    however, the field registry is requred during the startup, so we
    need to initialize it now.
    """
    field = _context.resolve(field)
    registerField(name, field)
    return []


def validator(_context, name, validator):
    """
    Note that most applications return an actual Action at this point;
    however, the validator registry is requred during the startup, so we
    need to initialize it now.
    """
    validator = _context.resolve(validator)
    registerValidator(name, validator)
    return []

