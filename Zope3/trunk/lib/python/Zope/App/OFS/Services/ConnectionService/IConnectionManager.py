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
"""
$Id: IConnectionManager.py,v 1.2 2002/12/09 15:26:42 ryzaja Exp $
"""
from Zope.App.RDB.IConnectionService import IConnectionService
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfigurable

class IConnectionManager(IConnectionService, IConfigurable):
    """A Connection Manager is a configurable connection service"""

    def queryConfigurations(connection_name):
        """Return an IConfigurationRegistry for a connection"""

    def createConfigurations(connection_name):
        """Create and return an IConfigurationRegistry a connection"""
