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
"""Permission grouping service for security managment"""

from Interface import Interface

class IPermissionGroupService(Interface):
    """Permission grouping service used to organize permissions in security
       managment
    """

    def getGroupsForPermission(permission):
        """Return a seq of IPermissionGroup objects that contain the
           specified permission, which must be an IPermission.
           An empty seq is returned if there are no groups containing that
           permission.
        """

    def getGroups():
        """Return a seq of all IPermissionGroups, or an empty seq if there are
           none"""

    def getGroup(gid):
        """Return the IPermissionGroup with the id gid. Raise NotFoundError
           if no such group exists"""

    
