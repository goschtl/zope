##############################################################################
#
# Copyright (c) 2005, 2006 Projekt01 GmbH and Contributors.
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

from zope.app.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.keyface import IKeyfaceType



def keyfaceDirective(_context, keyface, type=None):
    """Mark and register an new key interface."""

    # preconditions: type only once
    if IKeyfaceType.providedBy(keyface):
        raise ConfigurationError('Keyface %s already registered.' % keyface.__name__)

    if type is not None and not type.extends(IKeyfaceType):
        raise ConfigurationError('Type %s should extend %s.' % (type.__name__, IKeyfaceType.__name__))

    # assert type as soon as possible
    if type is None:
        type = IKeyfaceType
    
    alsoProvides(keyface, type)

    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (None, keyface, type),
        )
