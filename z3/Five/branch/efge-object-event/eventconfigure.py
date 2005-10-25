##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Use 'structured monkey patching' to enable zope.app.container event sending for
Zope 2 objects.

$Id$
"""

from event import doMonkies
from event import containerEventAwareClasses
from event import deprecatedManageAddDeleteClasses

def setContainerEvents(transitional):
    doMonkies(transitional)

def setContainerEventAware(class_):
    """Instances of the class will receive object events."""
    containerEventAwareClasses.append(class_)

def setDeprecatedManageAddDelete(class_):
    """Instances of the class will still see their old methods called."""
    deprecatedManageAddDeleteClasses.append(class_)

def containerEvents(_context, transitional):
    _context.action(
        discriminator=('five:containerEvents',),
        callable=setContainerEvents,
        args=(transitional,),
        )

def containerEventAware(_context, class_):
    _context.action(
        discriminator=('five:containerEventAware', class_),
        callable=setContainerEventAware,
        args=(class_,),
        )

def deprecatedManageAddDelete(_context, class_):
    _context.action(
        discriminator=('five:deprecatedManageAddDelete', class_),
        callable=setDeprecatedManageAddDelete,
        args=(class_,),
        )
