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


###############################################################################
#
# Base key interface related interfaces  
#
###############################################################################

class IKeyfaced(Interface):
    """Assert that a key interface can be looked up.

    The key interface must be provided by adaption to IKeyface."""



class IAttributeKeyfaced(IKeyfaced):
    """Provide the key interface within the __keyface__ attribute."""

    __keyface__ = Object(
        title=_('Key interface'),
        description=_('Key interface that allows to lookup ' +
                      'key-interface-specific informations such as ' +
                      'configurations providers.'),
        required=True,
        readonly=True,
        schema=IInterface)



class IKeyfaceType(IInterface):
    """Mark key interfaces.

    You can derive from this type to provide dedicated keyface types. A key 
    interface should only provide a single keyface type.
    """



class IKeyface(IKeyfaced):
    """Declare a key interface as component-specific key.

    You can use this key to lookup component-specific informations.
    """

    keyface = Object(
        title=_('Key interface'),
        description=_('Key interface of the adapted context.'),
        required=True,
        readonly=True,
        schema=IKeyfaceType)



class IKeyfaceDescription(IKeyface):
    """User description about the associated key interface."""

    label = TextLine(title=_('Label'),
        description=_('Label for associated key interface.'),
        required=True
        )  

    hint = Text(title=_('Hint'),
        description=_('Hint explaning the properties of the associated key interface.'),
        required=True
        )
