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

$Id: IPrincipal.py,v 1.2 2002/06/10 23:28:16 jim Exp $
"""

from Interface import Interface

class IPrincipal(Interface):
    """Provide information about principals.

    It is likely that IPrincipal objects will have associated
    views used to list principals in management
    interfaces. For example, a system in which other meta-data are
    provided for principals might extend IPrincipal and register a
    view for the extended interface that displays the extended
    information. We'll probably want to define a standard view
    name (e.g.  "inline_summary") for this purpose.
    """

    def getId():
        """Return a unique id string for the principal.
        """

    def getTitle():
        """Return a label for the principal

        The label will be used in interfaces to allow users to make
        security assertions (e.g. role or permission
        assignments) about principals.
        """
    def getDescription():
        """Return a description of the principal."""
