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

$Id: connection.py,v 1.3 2003/03/21 21:04:44 jim Exp $
"""
from zope.app.services.field import ComponentPath
from zope.app.interfaces.services import configuration 
from zope.app.interfaces.rdb import IZopeDatabaseAdapter

class IConnectionConfiguration(configuration.INamedComponentConfiguration):
    """Database Connection Configuration

    Connection configurations are dependent on the database adapters that they
    configure. They register themselves as component dependents.
    """
    
    componentPath = ComponentPath(
        type=IZopeDatabaseAdapter,
        title=u"Component path",
        description=u"The physical path to the component",
        required=True)
