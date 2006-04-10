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



class IInterfaceKeyed(Interface):
    """Provide an interface key by implementation or adaption."""



class IInterfaceKey(IInterfaceKeyed):
    """Declare an interface as information-specific-key."""

    interface = Object(
        title=_('Interface'),
        description=_('Interface marker that can be used as' +
                      'interface-specific-key to lookup informations.'),
        required=True,
        readonly=True,
        schema=IInterface)



class IInterfaceKeyDescription(IInterfaceKey):
    """Describe the associated interface key."""

    label = TextLine(title=_('Label'),
        description=_('Label for associated interface marker.'),
        required=True
        )  

    hint = Text(title=_('Hint'),
        description=_('Hint explaning the properties of the associated interface marker.'),
        required=True
        )
