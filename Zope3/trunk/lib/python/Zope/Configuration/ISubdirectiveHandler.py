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
"""Psuedo-directive (or meta-meta directive) to handle subdirectives

$Id: ISubdirectiveHandler.py,v 1.2 2002/09/03 16:07:08 jim Exp $
"""
from Interface import Interface

class ISubdirectiveHandler(Interface):
    """Handle subdirectives

    Provide methods for registered subdirectives. The methods are
    typically IEmptyDirective objects. They could, theoretically be
    INonEmptyDirective objects. 

    Also provide a call that can provide additional configuration
    actions. 
    
    """

    def __call__():
        """Return a sequence of configuration actions.
        
        See IEmptyDirective for a definition of configuration actions."""
