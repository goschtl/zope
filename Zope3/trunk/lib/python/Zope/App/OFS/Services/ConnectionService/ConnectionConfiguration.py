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
"""A configuration for a database adapter.

$Id: ConnectionConfiguration.py,v 1.1 2002/12/09 15:26:42 ryzaja Exp $
"""

from IConnectionConfiguration import IConnectionConfiguration
from Zope.App.OFS.Services.Configuration import ComponentConfiguration
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty

class ConnectionConfiguration(ComponentConfiguration):

    __doc__ = IConnectionConfiguration.__doc__
    
    __implements__ = (IConnectionConfiguration,
                      ComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('SQLDatabaseConnections')

    def __init__(self, connection_name, *args, **kw):
        self.connectionName = connection_name
        super(ConnectionConfiguration, self).__init__(*args, **kw)
