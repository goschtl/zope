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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: Package.py,v 1.2 2002/11/30 18:40:29 jim Exp $
"""
__metaclass__ = type

from Zope.App.OFS.Container.BTreeContainer import BTreeContainer

from IPackage import IPackage
from ConfigurationManager import ConfigurationManager


class Package(BTreeContainer):
    __implements__ = IPackage

    def __init__(self):
        super(Package, self).__init__()
        self.setObject('configure', ConfigurationManager())

    
