##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Interfaces for introspector related stuff.
"""
from zope.interface import Interface

class IGrokIntrospector(Interface):
    """An introspector for scanning the runtime system.
    """
    def __init__(obj, request):
        """An introspector must handle requests on arbitrary objects.

        It it the base for exploring the whole introspector facilities
        provided and should deliver content based on the request.

        How the request data is interpreted, is up to the introspector.
        """

class IGrokRegistryIntrospector(IGrokIntrospector):
    """An introspector for registries.
    """

class IGrokCodeIntrospector(IGrokIntrospector):
    """An introspector for packages, classes and other code.
    """

class IGrokContentBrowser(IGrokIntrospector):
    """A content browser
    """
