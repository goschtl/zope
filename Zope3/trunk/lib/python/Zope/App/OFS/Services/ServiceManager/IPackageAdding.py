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
"""IPackageAdding 

$Id: IPackageAdding.py,v 1.1 2002/12/23 08:15:38 srichter Exp $
"""
from Zope.App.OFS.Container.IAdding import IAdding

class IPackageAdding(IAdding):
    """The Package Adding is special, since it is not part of the content
    namespace, but has a similar functionality as a Folder. Therefore there
    are views that overlap; this interface was created so that there are no
    configuration conflicts."""

