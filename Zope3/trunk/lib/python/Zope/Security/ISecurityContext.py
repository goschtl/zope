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
from Interface import Interface
from Interface.Attribute import Attribute

class ISecurityContext( Interface ):
    """
        Capture transient request-specific security information.
    """
    Attribute( 'stack'
             , 'A stack of elements, each either be an ExecutableObject'
               'or a tuple consisting of an ExecutableObject and a'
               'custom SecurityPolicy.'
             )

    Attribute( 'user'
             , 'The AUTHENTICATED_USER for the request.'
             )

