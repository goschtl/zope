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
$Id: IBindingAware.py,v 1.5 2002/11/30 18:39:16 jim Exp $
"""

from Interface import Interface

class IBindingAware(Interface):
    
    def bound(name):
        """Inform a service components that it's providing a service

        Called when an immediately-containing service manager binds
        this object to perform the named service.
        """
    
    def unbound(name):
        """Inform a service components that it's no longer providing a service

        Called when an immediately-containing service manager unbinds
        this object from performing the named service.
        """
