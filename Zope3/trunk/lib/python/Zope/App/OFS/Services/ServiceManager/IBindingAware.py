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

Revision information:
$Id: IBindingAware.py,v 1.2 2002/06/10 23:28:12 jim Exp $
"""

from Interface import Interface

class IBindingAware(Interface):
    
    def bound(name):
        """Called when an immediately-containing service manager binds this object to
        perform the named service"""
    
    def unbound(name):
        """Called when an immediately-containing service manager unbinds this object
        from performing the named service"""