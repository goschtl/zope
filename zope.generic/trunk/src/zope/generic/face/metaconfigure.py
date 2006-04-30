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

from zope.component import provideUtility
from zope.component import queryUtility
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.face import IConfaceType
from zope.generic.face import IKeyfaceType
from zope.generic.face import INoKeyface
from zope.generic.face.base import GlobalInformationProvider
from zope.generic.face.base import LocalInformationProvider
from zope.generic.face.helper import toDottedName


def ensureInformationProvider(conface, keyface, context=None):
    """Provide an information provider."""

    # preconditions
    if not IConfaceType.providedBy(conface):
        raise TypeError('Conface requires %.' % IConfaceType.__name__)

    if not IKeyfaceType.providedBy(keyface):
        raise TypeError('Keyface requires %.' % IKeyfaceType.__name__)

    # essentials
    name = toDottedName(keyface)

    provider = queryUtility(conface, name, context=context)

    if not provider:
        
        if context is None:
            provider = GlobalInformationProvider(conface, keyface)
            provideUtility(provider, conface, name=name)
        
        else:
            provider = LocalInformationProvider(conface, keyface)
            context.registerUtility(provider, conface, name=name)



def keyfaceDirective(_context, keyface, type=None):
    """Type and register an new key interface."""

    # context can never be key interface and key can never be context interface
    if keyface and IConfaceType.providedBy(keyface):
        raise ConfigurationError('Key interface %s can not be registered as context interface too.' % keyface.__name__)

    # provide type as soon as possilbe
    provideInterface(None, keyface, IKeyfaceType)

    if type:
        # provide additional interface utility
        if not IConfaceType.providedBy(type):
            provideInterface(None, keyface, type)

        # provide global information provider
        else:
            alsoProvides(keyface, type)
            ensureInformationProvider(type, keyface)



def confaceDirective(_context, conface, type=None):
    """Type and register an new context interface."""

    # context can never be key interface and key can never be context interface
    if conface and IKeyfaceType.providedBy(conface):
        raise ConfigurationError('Context interface %s can not be registered as key interface too.' % conface.__name__)

    # provide type as soon as possilbe
    provideInterface(None, conface, IConfaceType)

    # provide additional interface utility
    if type:
        provideInterface(None, conface, type)



def faceDirective(_context, keyface=None, conface=None, type=None):
    """Type and register an new key or context interface."""

    # preconditions
    # register only key or context interface
    if keyface and conface:
        raise ConfigurationError('Cannot register a key or a context interface at the same time.')
    
    if keyface:
        keyfaceDirective(_context, keyface, type)

    else:
        confaceDirective(_context, conface, type)
