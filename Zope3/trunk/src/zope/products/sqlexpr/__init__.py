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
"""SQL Expression Package

$Id: __init__.py,v 1.1 2004/02/11 17:43:29 philikon Exp $
"""
from zope.app.pagetemplate.engine import Engine
from sqlexpr import SQLExpr

# XXX: Almost a classic monkey patch. We really should have a ZCML directive
# for this.
Engine.registerType('sql', SQLExpr)
