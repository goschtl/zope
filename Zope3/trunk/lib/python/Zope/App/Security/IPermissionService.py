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

$Id: IPermissionService.py,v 1.3 2002/12/01 10:31:59 jim Exp $
"""

from Interface import Interface

class IPermissionService(Interface):

    """Manage information about permissions
    
     'IPermissionService' objects are used to implement
     permission-definition services. Because they implement services,
     they are expected to collaborate with services in other
     contexts. Client code doesn't search a context and call multiple
     services. Instead, client code will call the most specific
     service in a place and rely on the service to delegate to other
     services as necessary.

     The interface doesn't include methods for data
     management. Services may use external data and not allow
     management in Zope. Similarly, the data to be managed may vary
     with different implementations of a service.
     """

    def getPermission(permission_id):
        """Get permission information

        Return an 'IPermission' object for the
        given permission id.  Return None if there is no permission defined
        """

    def getPermissions():
        """Get the defined permissions

        Return a sequence of the permissions
        (IPermission objects) defined in the place containing the
        service.
        """
