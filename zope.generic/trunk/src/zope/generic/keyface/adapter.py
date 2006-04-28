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

from zope.component import adapts
from zope.interface import implements
from zope.location import Location

from zope.generic.keyface import IAttributeKeyfaced
from zope.generic.keyface import IKeyface



class KeyfaceForAttributeKeyfaced(Location):
    """Adapts IAttributeKeyfaced to IKeyface.

    You can adapt IKeyface if you provide IAttributeKeyfaced:

        >>> class AnyAttributeKeyfaced(object):
        ...    def __init__(self, keyface):
        ...         self.__keyface__ = keyface

        >>> fake_keyface = object()
        >>> any = AnyAttributeKeyfaced(fake_keyface)

        >>> KeyfaceForAttributeKeyfaced(any).keyface == fake_keyface
        True
        >>> IKeyface.providedBy(KeyfaceForAttributeKeyfaced(any))
        True

"""

    implements(IKeyface)
    adapts(IAttributeKeyfaced)

    def __init__(self, context):
        self.context = context

    @property
    def keyface(self):
        return self.context.__keyface__
