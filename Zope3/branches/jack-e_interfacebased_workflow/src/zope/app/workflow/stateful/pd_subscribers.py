##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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

"""Process definition permissions changed subscribers

$Id:$
"""

def processDefinitionAddPermissionsSusbcriber(event):
    """Add permissions to the process definition permissions mapping
    """
    pd = event.object
    permissions_to_add = event.permissions_to_add
    for permission in permissions_to_add:
        pd.addProcessPermission(permission)

def processDefinitionDelPermissionsSusbcriber(event):
    """Del permissions to the process definition permissions mapping
    """
    pd = event.object
    permissions_to_remove = event.permissions_to_remove
    for permission in permissions_to_remove:
        pd.delProcessPermission(permission)
