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
"""ZCML configuration directives for configuring the default zope:
namespace in TALES.

$Id$
"""
from zope.app.pagetemplate.engine import Engine, _Engine
from zope.testing.cleanup import addCleanUp

def namespace(_context, prefix, interface):
    _context.action(
        discriminator = ("tales:namespace", prefix),
        callable = Engine.registerFunctionNamespace,
        args = (prefix, lambda ob: interface(ob)),
        )

def expressiontype(_context, name, handler):
    _context.action(
        discriminator = ("tales:expressiontype", name),
        callable = Engine.registerType,
        args = (name, handler)
        )


def clear():
    Engine.__init__()
    _Engine(Engine)

addCleanUp(clear)
