##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adding View for IPackage

$Id: PackageAdding.py,v 1.1 2002/12/23 08:15:38 srichter Exp $
"""
from Zope.Publisher.VFS.VFSView import VFSView
from Zope.App.OFS.Container.Views.VFS.Adding import Adding
from Zope.App.OFS.Services.ServiceManager.IPackageAdding import IPackageAdding

class PackageAdding(Adding):

    __implements__ =  IPackageAdding, VFSView.__implements__
