##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Case-insensitive traverser and folder interfaces.

$Id: interfaces.py,v 1.1 2004/02/13 23:28:45 srichter Exp $
"""
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.interfaces.content.folder import IFolder

class ICaseInsensitiveContainerTraverser(IBrowserPublisher):
    """Case-Insensitive Traverser"""

    def guessTraverse(name):
        """Try to travers 'name' using a case insensitive match."""


class ICaseInsensitiveFolder(IFolder):
    """Marker for folders whose contained items keys are case insensitive.

    When traversing in this folder, all names will be converted to lower
    case. For example, if the traverser requests an item called 'Foo', in
    reality item 'foo' is looked up in the container."""
        
