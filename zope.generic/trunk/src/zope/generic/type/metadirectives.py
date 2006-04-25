##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.i18n import ZopeMessageFactory as _
from zope.app.security.fields import Permission
from zope.configuration.fields import Bool
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

from zope.generic.factory.metadirectives import IBaseFactoryDirective
from zope.generic.informationprovider.metadirectives import IBaseInformationProviderDirective
from zope.generic.operation.metadirectives import IBaseOperationDirective

    

class ITypeDirective(IBaseInformationProviderDirective):
    """Declare attriubtes of the type directive.

    Register an type information and a type factory.
    """



class IFactorySubdirective(IBaseFactoryDirective, IBaseOperationDirective):
    """Provide an factory for the type."""



class IConfigurationAdapterSubdirective(Interface):
    """Provide an adapter to a certain configuration."""

    keyface = GlobalInterface(
        title=_('Configuration Key Interface3'),
        description=_('Configuration interface defining adapter interface.'),
        required=True
        )

    class_ = GlobalObject(
        title=_('Adapter class'),
        description=_('If not declared a generic implementation will be used.'),
        required=False
        )

    writePermission = Permission(
        title=_('Write Permission'),
        description=_('Specifies the permission by id that will be required ' +
            ' to mutate the attributes and methods specified.'),
        required=False,
        )

    readPermission = Permission(
        title=_('Read Permission'),
        description=_('Specifies the permission by id that will be required ' +
            ' to accessthe attributes and methods specified.'),
        required=False,
        )

