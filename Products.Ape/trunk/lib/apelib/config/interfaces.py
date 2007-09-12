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
"""Configuration interfaces.

$Id$
"""

from Interface import Interface

class IDirective(Interface):
    """A configuration directive.
    """

    def get_unique_key():
        """Returns a key that distinguishes this directive from all others.

        This is used for detecting conflicting directives.  The
        returned key must be hashable.  It normally includes the type
        (class or interface) of the directive.  If this returns None,
        the directive conflicts with nothing.
        """

    def index(tables):
        """Adds self to a table.

        tables is a mapping from table name to table.  The table name
        is usually the class of the directive.
        """

# IAssembler, IComponentSystem, etc.

