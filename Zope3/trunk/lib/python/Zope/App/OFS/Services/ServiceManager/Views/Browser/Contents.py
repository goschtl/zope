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
""" Define view component for service manager contents.

$Id: Contents.py,v 1.2 2002/06/10 23:28:13 jim Exp $
"""

from Zope.App.OFS.Container.Views.Browser.Contents import Contents
from Zope.App.OFS.Content.Folder.Views.Browser.FolderContents import FolderContents
from Interface.Implements import flattenInterfaces, objectImplements

class ServiceManagerContents(Contents):

    def _extractContentInfo( self, item ):
        info = Contents._extractContentInfo(self, item)
        implements = objectImplements(info['object'])
        interfaces = flattenInterfaces(implements)

        interface_names = [ x.getName() for x in interfaces
                                         if x.getName() != 'Interface' ]
        info['interfaces'] = interface_names

        return info

