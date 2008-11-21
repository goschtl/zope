##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
""" 

$Id: installer.py 1472 2008-02-18 11:35:13Z fafhrd91 $
"""
from zope import interface
from z3ext.controlpanel.interfaces import IConfiglet


class ProductsInstaller(object):

    def isAvailable(self):
        if not len(self):
            return False

        return super(ProductsInstaller, self).isAvailable()
