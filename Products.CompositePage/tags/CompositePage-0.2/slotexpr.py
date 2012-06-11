##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source 
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this 
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Support for 'slot:' expression type in ZPT.

$Id: slotexpr.py,v 1.5 2004/05/03 16:02:40 sidnei Exp $
"""

import re

from Products.PageTemplates.TALES import CompilerError, Default

from interfaces import IComposite

name_re = re.compile("\s*([a-zA-Z][a-zA-Z0-9_]*)")
class_name_re = re.compile("\s*[(]([a-zA-Z][a-zA-Z0-9_]*)[)]")
title_re = re.compile("\s*[']([^']+)[']")


class SlotExpr:
    """Slot expression type.

    Provides a concise syntax for specifying composite slots in
    ZPT.  An example slot expression, in context of ZPT:

    <div tal:replace="slot: slot_name(class_name) 'Title'" />
    """

    def __init__(self, name, expr, engine):
        self._s = s = expr
        mo = name_re.match(s)
        if mo is None:
            raise CompilerError('Invalid slot expression "%s"' % s)
        self._name = mo.group(1)
        s = s[mo.end():]
        mo = class_name_re.match(s)
        if mo is not None:
            self._class_name = mo.group(1)
            s = s[mo.end():]
        else:
            self._class_name = None
        mo = title_re.match(s)
        if mo is not None:
            self._title = mo.group(1)
            s = s[mo.end():]
        else:
            self._title = None
        if s.strip():
            # Can't interpret some of the expression
            raise CompilerError(
                'Slot expression syntax error near %s' % repr(s))
    
    def __call__(self, econtext):
        context = econtext.contexts.get('options')
        if context is None:
            raise RuntimeError("Could not find options")
        composite = context.get('composite')
        if IComposite.isImplementedBy(composite):
            slot = composite.slots.get(
                self._name, self._class_name, self._title)
            # Render the slot
            return "".join(slot.multiple())
        else:
            # Show the default content
            return Default

    def __repr__(self):
        return 'slot:%s' % self._s


def registerSlotExprType():
    # Register the 'slot:' expression type.
    from Products.PageTemplates.Expressions import getEngine
    # Avoid registering twice.
    engine = getEngine()
    if not engine.getTypes().has_key('slot'):
        engine.registerType('slot', SlotExpr)
