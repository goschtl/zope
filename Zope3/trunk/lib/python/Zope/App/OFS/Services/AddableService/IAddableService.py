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
generic AddableService

$Id: IAddableService.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""
from Interface import Interface

class IAddableService(Interface):
    """The common denominator for all addables services.  Addables are
    the Zope-specific front end for the factory service.  The
    functionality relies on the factory service and on the IContainer
    interface"""
    
    def getAddables(container):
        """returns the addables available from this service and its
        parents for the service's context.
        
        By default, it is limited by what factory names are also
        available in the same context; and further limited by what
        addables and factories are registered to be added to the
        interfaces implemented by the container; and, if the container
        implements IWriteContainer, further limited by what interfaces
        the container supports in its getAddableInterfaces method."""

