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
from zope.interface import implements

from zope.generic.keyface import IKeyface
from zope.generic.keyface import IKeyfaceDescription



class Keyface(object):
    """Key interface mixin for key interface attribute implementations.
    
    You can mixin this class if you like to provide IKeyface for
    IAttributeKeyfaced implementations:

        >>> class AnyAttributeKeyfaced(Keyface):
        ...    def __init__(self, keyface):
        ...         self.__keyface__ = keyface

        >>> fake_keyface = object()
        >>> any = AnyAttributeKeyfaced(fake_keyface)
        >>> any.__keyface__ == fake_keyface
        True

    You get only the following method decorator for free :):

        >>> any.keyface == fake_keyface
        True
            
    """

    implements(IKeyface)

    @property
    def keyface(self):
        return self.__keyface__



class KeyfaceDescription(Keyface):
    """Key interface description mixin."""

    implements(IKeyfaceDescription)

    def __init__(self, keyface, label=None, hint=None):
        self.__keyface__ = keyface

        if label is None:
            self.label = _(keyface.__name__)
        else:
            self.label = label

        if hint is None:
            self.hint = _(keyface.__doc__)
        else:
            self.hint = hint
