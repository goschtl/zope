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
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import PythonIdentifier
from zope.configuration.fields import Tokens
from zope.interface import Interface
from zope.schema import DottedName
from zope.security.zcml import Permission


class IForAdapterDirective(Interface):
    """Declare the for attribute."""

    for_ = Tokens(
        title=_('Specifications to be adapted'),
        description=_('This should be a list of interfaces or classes.'),
        required=False,
        value_type=GlobalObject(missing_value=object())
        )



class IOthersAdapterDirective(Interface):
    """Declare all others attributes."""

    provides = GlobalInterface(
        title=_('Provided Interface'),
        description=_('The interface that is provided by the adapter.'),
        required=True
        )

    class_ = GlobalObject(
        title=_('Adapter class'),
        description=_('If not declared a generic implementation will be used.'),
        required=False
        )

    writePermission = Permission(
        title=_('Write Permission'),
        description=_('Specifies the permission by id that will be required '
            'to mutate the attributes and methods specified.'),
        required=False,
        )

    readPermission = Permission(
        title=_('Read Permission'),
        description=_('Specifies the permission by id that will be required '
            'to accessthe attributes and methods specified.'),
        required=False,
        )

    attributes = Tokens(
        title=_('Attributes and methods'),
        description=_('This is a list of attributes and methods '
            'that can be accessed.'),
        required=False,
        value_type=PythonIdentifier(),
        )

    set_attributes = Tokens(
        title=_('Attributes that can be set'),
        description=_('This is a list of attributes that can be '
            'modified/mutated.'),
        required=False,
        value_type=PythonIdentifier(),
        )

    key = DottedName(
        title=_('Interface'),
        description=_('Interface referencing a configuraiton.'),
        required=False
        )

    informationProviders = Tokens(
        title=_('Information Providers'),
        description=_('This information provides should be invoke '
            'to lookup informations such as configurations and annotations.'),
        required=False,
        value_type=GlobalInterface(),
        )


class IAdapterDirective(IForAdapterDirective, IOthersAdapterDirective):
    """Provide trusted locatable adapter including permissions."""

 

