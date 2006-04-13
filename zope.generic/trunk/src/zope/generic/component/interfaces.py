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
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.schema import Object
from zope.schema import Text
from zope.schema import TextLine



class IKeyInterfaceProvider(Interface):
    """Assert that a key interface can be looked up.

    The key interface must be provided by adaption to IKeyInterface."""



class IKeyInterfaceAttributeProvider(IKeyInterfaceProvider):
    """Provide the key interface within an attribute.

    The key interface is stored within the __key_interface__ attribute.
    """



class IKeyInterface(IKeyInterfaceProvider):
    """Declare a key interface as component-specific key.

    You can use this key to lookup component-specific informations.
    """

    interface = Object(
        title=_('Interface'),
        description=_('Interface marker that can be used as' +
                      'interface-specific-key to lookup informations.'),
        required=True,
        readonly=True,
        schema=IInterface)



class IKeyInterfaceDescription(IKeyInterface):
    """Describe the associated interface key."""

    label = TextLine(title=_('Label'),
        description=_('Label for associated interface marker.'),
        required=True
        )  

    hint = Text(title=_('Hint'),
        description=_('Hint explaning the properties of the associated interface marker.'),
        required=True
        )
