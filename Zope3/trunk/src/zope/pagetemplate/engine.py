##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Expression engine configuration and registration.

Each expression engine can have its own expression types and base names.

$Id: engine.py,v 1.2 2002/12/25 14:15:13 jim Exp $
"""

from zope.pagetemplate.tales import ExpressionEngine, RegistrationError
from zope.pagetemplate.expressions import PathExpr, StringExpr, NotExpr, DeferExpr
from zope.pagetemplate.expressions import SimpleModuleImporter
from zope.pagetemplate.pythonexpr import PythonExpr

def Engine():
    e = ExpressionEngine()
    reg = e.registerType
    for pt in PathExpr._default_type_names:
        reg(pt, PathExpr)
    reg('string', StringExpr)
    reg('python', PythonExpr)
    reg('not', NotExpr)
    reg('defer', DeferExpr)
    e.registerBaseName('modules', SimpleModuleImporter())
    return e

Engine = Engine()
