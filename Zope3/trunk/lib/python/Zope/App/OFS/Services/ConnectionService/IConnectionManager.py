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
"""
$Id: IConnectionManager.py,v 1.1 2002/06/24 16:18:50 srichter Exp $
"""
from Zope.App.OFS.Container.IContainer import IContainer
from Zope.App.RDB.IConnectionService import IConnectionService

class IConnectionManager(IContainer, IConnectionService):
    """TTW object that manages RDBMS connections"""

__doc__ = IConnectionManager.__doc__ + __doc__
