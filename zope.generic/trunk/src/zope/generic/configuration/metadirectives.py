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
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.interface import Interface



class IConfigurationAdapterDirective(Interface):
    """Provide an adapter to a certain configuration."""

    keyface = GlobalInterface(
        title=_('Key Interface3'),
        description=_('Configuration interface defining adapter interface.'),
        required=True
        )

    provides = GlobalInterface(
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

