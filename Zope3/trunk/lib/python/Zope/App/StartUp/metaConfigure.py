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

$Id: metaConfigure.py,v 1.2 2002/11/19 23:25:14 jim Exp $
"""

from SiteDefinition import SiteDefinition
from Zope.Configuration.Action import Action
from RequestFactory import RequestFactory
import RequestFactoryRegistry 
from ServerType import ServerType
import ServerTypeRegistry 

defineSite = SiteDefinition


def registerRequestFactory(_context, name, publication, request):
    """ """
    publication = _context.resolve(publication)
    request = _context.resolve(request)
    request_factory = RequestFactory(publication, request)

    return [
        Action(
            discriminator = name,
            callable = RequestFactoryRegistry.registerRequestFactory,
            args = (name, request_factory,),
            )
        ]


def registerServerType(_context, name, factory, requestFactory, logFactory,
                       defaultPort, defaultVerbose):
    """ """
    factory = _context.resolve(factory)
    logFactory = _context.resolve(logFactory)

    if defaultVerbose.lower() == 'true':
        defaultVerbose = 1
    else:
        defaultVerbose = 0

    defaultPort = int(defaultPort)

    server_type = ServerType(name, factory, requestFactory, logFactory,
                             defaultPort, defaultVerbose)
    

    return [
        Action(
            discriminator = name,
            callable = ServerTypeRegistry.registerServerType,
            args = (name, server_type),
            )
        ]

