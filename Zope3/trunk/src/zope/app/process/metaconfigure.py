##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
This module handles the :startup directives.

$Id: metaconfigure.py,v 1.2 2003/06/25 15:29:32 fdrake Exp $
"""

from zope.configuration.action import Action
from zope.app.process import requestfactoryregistry
from zope.app.process import servertyperegistry
from zope.app.process.requestfactory import RequestFactory
from zope.app.process.servertype import ServerType


def registerRequestFactory(_context, name, request=None, publication=None,
                           factory=None):

    if factory:
        if request or publication:
            raise ValuesError(
                """Can't provide a request or publication (factory) if you
                provide a (request) factory""")
        request_factory = _context.resolve(factory)

    else:
        publication = _context.resolve(publication)
        request = _context.resolve(request)
        request_factory = RequestFactory(publication, request)

    return [
        Action(
            discriminator = name,
            callable = requestfactoryregistry.registerRequestFactory,
            args = (name, request_factory,),
            )
        ]


def registerServerType(_context, name, factory, requestFactory, logFactory,
                       defaultPort, defaultVerbose):
    factory = _context.resolve(factory)
    logFactory = _context.resolve(logFactory)

    if defaultVerbose.lower() == 'true':
        defaultVerbose = True
    else:
        defaultVerbose = False

    defaultPort = int(defaultPort)

    server_type = ServerType(name, factory, requestFactory, logFactory,
                             defaultPort, defaultVerbose)

    return [
        Action(
            discriminator = name,
            callable = servertyperegistry.registerServerType,
            args = (name, server_type),
            )
        ]
