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

$Id: connection.py,v 1.7 2003/04/24 15:07:25 gvanrossum Exp $
"""

from zope.schema import TextLine
from zope.app.interfaces.services.configuration import IComponentConfiguration
from zope.app.interfaces.services.configuration import ComponentPath
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.rdb import IConnectionService
from zope.app.interfaces.services.configuration \
        import INameComponentConfigurable

class IConnectionConfiguration(IComponentConfiguration):
    """Database Connection Configuration

    Connection configurations are dependent on the database adapters that they
    configure. They register themselves as component dependents.
    """

    name = TextLine(title=u"Name",
                    description=u"The name that is registered",
                    readonly=True,
                    required=True,
                    min_length=1,
                    )
    
    componentPath = ComponentPath(
        title=u"Component path",
        description=u"The physical path to the component",
        readonly=True,
        required=True)


class ILocalConnectionService(IConnectionService, INameComponentConfigurable):
    """A local (placeful) connection service"""
