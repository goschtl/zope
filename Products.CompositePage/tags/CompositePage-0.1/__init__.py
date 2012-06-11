##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""CompositePage product initialization.

$Id: __init__.py,v 1.1 2003/09/26 21:21:05 shane Exp $
"""

import tool, composite, slot, transformers


def initialize(context):

    tool.registerTransformer("common", transformers.CommonTransformer())
    tool.registerTransformer("zmi", transformers.ZMITransformer())

    context.registerClass(
        tool.CompositeTool,
        constructors=(tool.manage_addCompositeTool,),
        icon="www/comptool.gif",
        )

    context.registerClass(
        composite.Composite,
        constructors=(composite.addCompositeForm,
                      composite.manage_addComposite,
                      ),
        icon="www/composite.gif",
        )

    context.registerClass(
        slot.Slot,
        constructors=(slot.addSlotForm,
                      slot.manage_addSlot,
                      slot.manage_generateSlots,
                      ),
        visibility=None,
        )

