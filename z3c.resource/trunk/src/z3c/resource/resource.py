##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

import zope.interface
from zope.app.container import btree
from z3c.resource import interfaces


class Resource(btree.BTreeContainer, object):
    """Resource implementation.

    >>> resource = Resource()

    Such a resource provides:

    >>> interfaces.IResource.providedBy(resource)
    True

    >>> from zope.app.container.interfaces import IContainer
    >>> IContainer.providedBy(resource)
    True

    """

    zope.interface.implements(interfaces.IResource)
