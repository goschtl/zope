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

$Id: connection.py,v 1.2 2002/12/25 14:13:02 jim Exp $
"""

from zope.app.interfaces.services.configuration \
     import INamedComponentConfiguration

class IConnectionConfiguration(INamedComponentConfiguration):
    """Database Connection Configuration

    Connection configurations are dependent on the database adapters that they
    configure. They register themselves as component dependents.
    """
