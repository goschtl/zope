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
"""A registration for a database adapter.

$Id: connection.py,v 1.11 2003/08/08 00:14:41 srichter Exp $
"""
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.services.registration import IComponentRegistration
from zope.app.interfaces.services.registration import ComponentPath
from zope.app.interfaces.rdb import IConnectionService
from zope.app.interfaces.services.registration \
     import INameComponentRegistry
from zope.schema import TextLine

class IConnectionRegistration(IComponentRegistration):
    """Database Connection Registration

    Connection registrations are dependent on the database adapters that they
    configure. They register themselves as component dependents.
    """

    name = TextLine(
        title=_("Name"),
        description=_("The name that is registered"),
        readonly=True,
        required=True,
        min_length=1,
        )

    componentPath = ComponentPath(
        title=_("Component path"),
        description=_("The physical path to the component"),
        readonly=True,
        required=True)


class ILocalConnectionService(IConnectionService, INameComponentRegistry):
    """A local (placeful) connection service"""

