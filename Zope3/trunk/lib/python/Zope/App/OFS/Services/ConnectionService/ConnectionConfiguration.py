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

$Id: ConnectionConfiguration.py,v 1.2 2002/12/12 11:32:31 mgedmin Exp $
"""

from IConnectionConfiguration import IConnectionConfiguration
from Zope.App.OFS.Services.Configuration import NamedComponentConfiguration
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty

class ConnectionConfiguration(NamedComponentConfiguration):

    __doc__ = IConnectionConfiguration.__doc__

    __implements__ = (IConnectionConfiguration,
                      NamedComponentConfiguration.__implements__)

    status = ConfigurationStatusProperty('SQLDatabaseConnections')

    label = "Connection"

    def __init__(self, *args, **kw):
        super(ConnectionConfiguration, self).__init__(*args, **kw)
