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
"""Interface definition for the Zope convenience API module

$Id: zapi.py,v 1.7 2003/06/12 09:33:47 jim Exp $
"""
from zope.component.interfaces import IComponentArchitecture
from zope.app.interfaces.context import IContextWrapper
from zope.context.interfaces import IWrapperIntrospection
from zope.context.interfaces import IContextAwareDescriptorSupport
from zope.app.interfaces.traversing import ITraversalAPI

class IZAPI(
    IComponentArchitecture,
    IContextWrapper,
    IWrapperIntrospection,
    IContextAwareDescriptorSupport,
    ITraversalAPI,
    ):
    """Convenience API for use with Zope applications.
    """

    def name(obj):
        """Return an object's name

        This is the name the object is stored under in the container
        it was accessed in.  If the name is unknown, None is returned.
        """
