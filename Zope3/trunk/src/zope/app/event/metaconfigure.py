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
$Id: metaconfigure.py,v 1.5 2004/03/02 18:50:59 philikon Exp $
"""

from zope.app.event.interfaces import IEvent
from globalservice import globalSubscribeMany

directive_counter = 0
def subscribe(_context, subscriber, event_types=[IEvent], filter=None):
    global directive_counter
    directive_counter += 1

    _context.action(
        # subscriptions can never conflict
        discriminator = ('subscribe', directive_counter),
        callable = globalSubscribeMany,
        args = (subscriber, event_types, filter)
        )
