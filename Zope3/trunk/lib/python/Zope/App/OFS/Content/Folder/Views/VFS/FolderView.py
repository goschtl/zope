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
"""VFS-View for IFolder

$Id: FolderView.py,v 1.1 2002/12/20 10:31:47 srichter Exp $
"""

from Zope.App.OFS.Container.Views.VFS.VFSContainerView import \
     VFSContainerView

class FolderView(VFSContainerView):
    """Specific Folder VFS view."""

    __implments__ = VFSContainerView.__implements__

    _directory_type = 'Folder'
