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

$Id: metaconfigure.py,v 1.3 2003/02/07 15:59:45 jim Exp $
"""

from zope.app.startup.sitedefinition import SiteDefinition
from zope.configuration.action import Action
from zope.app.startup import requestfactoryregistry
from zope.app.startup import servertyperegistry
from zope.app.startup.requestfactory import RequestFactory
from zope.app.startup.servertype import ServerType

defineSite = SiteDefinition


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
