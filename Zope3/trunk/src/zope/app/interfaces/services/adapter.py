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
"""Service interfaces

$Id: adapter.py,v 1.1 2003/03/11 16:15:52 jim Exp $
"""

from zope.app.interfaces.services.configuration import IConfiguration
from zope.app.component.interfacefield import InterfaceField
from zope.app.security.permission import PermissionField
from zope.schema import BytesLine, TextLine
from zope.interface import Interface

class IAdapterConfigurationInfo(Interface):

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being adapted",
        readonly = True,
        basetype = None
        )

    providedInterface = InterfaceField(
        title = u"Provided interface",
        description = u"The interface provided by the adapter",
        readonly = True,
        required = True,
        )

    adapterName = TextLine(
        title=u"The name of the adapter",
        readonly=True,
        required=False,
        )

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the adapter",
        readonly = True,
        required = True,
        )

    permission = PermissionField(
        title=u"The permission required to use the adapter",
        readonly=False,
        required=False,
        )
        

class IAdapterConfiguration(IConfiguration, IAdapterConfigurationInfo):

    def getAdapter(object):
        """Return an adapter for the object

        The adapter is computed by passing the object to the
        registered factory.
        """
