##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Meta-Configuration Handler for the ``zope:tutorial`` directive.

$Id: $
"""
__docformat__ = 'restructuredtext'

from zope.tutorial import tutorial, interfaces
from zope.app.component import metaconfigure

def tutorial(_context, name, title, path):
    """Register a tutorial"""

    metaconfigure.utility(
        _context,
        provides = interfaces.ITutorial,
        component = tutorial.Tutorial(title, path),
        name = name)
