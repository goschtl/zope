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
"""VFS-View for IPackage

$Id: PackageView.py,v 1.1 2002/12/23 08:15:38 srichter Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from Zope.ComponentArchitecture import getAdapter
from Zope.App.DublinCore.IZopeDublinCore import IZopeDublinCore
from Zope.App.OFS.Container.Views.VFS.VFSContainerView import \
     VFSContainerView

class PackageView(VFSContainerView):
    """Specific Package VFS view."""

    __implments__ = VFSContainerView.__implements__

    _directory_type = 'Package'

