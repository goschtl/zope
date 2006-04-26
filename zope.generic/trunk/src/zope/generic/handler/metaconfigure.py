##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.component.metaconfigure import subscriber

from zope.generic.keyface import IKeyfaceType
from zope.generic.operation.api import assertOperation


def handlerDirective(_context, keyface, event, operations=(), input=None):
    """Provide a generic trusted handler."""

    # TODO: to be finished...
    if input:
        raise NotImplementedError('Missing feature: You cannot use the input attribute yet.')

    # evaluate the operation
    operation = assertOperation(operations, keyface, input, None)

    def handler(component, event):
        operation(component, event)

    subscriber(_context, for_=[keyface, event], factory=None, handler=handler, 
        provides=None, permission=None, trusted=True, locate=False)

