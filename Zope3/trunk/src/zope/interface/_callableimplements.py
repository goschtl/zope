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
"""Hack^H^H^Hook up zope.interface.implements as a callable module.

$Id: _callableimplements.py,v 1.2 2003/05/03 16:35:14 jim Exp $
"""
import sys
import zope.interface.implements
from zope.interface.declarations import _implements, ImplementsSpecification

Module = sys.__class__

class ImplementsModule:

    def __init__(self):
        self.__dict__.update(sys.modules['zope.interface.implements'].__dict__)

    def __call__(self, *interfaces):
        return _implements("implements", ImplementsSpecification(*interfaces))

def hookup():
    global _old
    _old = sys.modules['zope.interface.implements']
    sys.modules['zope.interface.implements'] = ImplementsModule()

    
