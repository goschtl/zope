##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

import bobo

import os

from z3c.bobopublisher.interfaces import IDefaultViewName, IRequest, \
    IGETRequest, IPOSTRequest, IPUTRequest, IDELETERequest
from z3c.bobopublisher.resources import Directory, File

from zope.component.zcml import handler
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface
from zope.location.interfaces import IRoot
from zope.security.checker import CheckerPublic
from zope.security.interfaces import Unauthorized
from zope.security.management import checkPermission


def _page_factory(class_, name, permission, attribute=None):
    def factory(context, request):
        if permission is not None and \
           not checkPermission(permission, context):
            raise Unauthorized(context, name, permission)
        if attribute is not None:
            return class_(context, request, attribute)
        return class_(context, request)
    return factory


def page(_context, name='index.html', for_=None, class_=None, permission=None,
    methods=None, attribute=None):
    requests = []
    if methods == None:
        requests.append(IRequest)
    else:
        for m in methods:
            if m == 'GET':
                requests.append(IGETRequest)
            elif m == 'POST':
                requests.append(IPOSTRequest)
            elif m == 'PUT':
                requests.append(IPUTRequest)
            elif m == 'DELETE':
                requests.append(IDELETERequest)
    if attribute is not None and not hasattr(class_, attribute):
        raise ConfigurationError("The provided class doesn't have the "
            "specified attribute")
    elif permission is not None or attribute is not None:
        if permission == 'zope.Public':
            permission = CheckerPublic
        class_ = _page_factory(class_, name, permission, attribute)
    for request in requests:
        _context.action(
            discriminator = ('page', for_, name),
            callable = handler,
            args = ('registerAdapter',
                class_, (for_, request), Interface, name, _context.info,
            ),
        )

def resources(_context, name, directory, for_=IRoot, permission=None):
    if not os.path.isdir(directory):
        raise ConfigurationError('Directory %s does not exist' % directory)
    if permission == 'zope.Public':
        permission = CheckerPublic
    def resourcesFactory(context, request):
        if not checkPermission(permission, context):
            raise Unauthorized(context, name, permission)
        return Directory(directory)
    _context.action(
        discriminator = ('page', for_, name),
        callable = handler,
        args = ('registerAdapter',
            resourcesFactory, (for_, IGETRequest), Interface, name,
            _context.info,
        ),
    )


def resource(_context, name, file, for_=IRoot, permission=None):
    if not os.path.isfile(file):
        raise ConfigurationError('File %s does not exist' % directory)
    if permission == 'zope.Public':
        permission = CheckerPublic
    def resourceFactory(context, request):
        if not checkPermission(permission, context):
            raise Unauthorized(context, name, permission)
        return File(file)
    _context.action(
        discriminator = ('page', for_, name),
        callable = handler,
        args = ('registerAdapter',
            resourceFactory, (for_, IGETRequest), Interface, name,
            _context.info,
        ),
    )


def defaultView(_context, name, for_):
    _context.action(
        discriminator = ('defaultView', for_, name),
        callable = handler,
        args = ('registerAdapter',
            lambda x: name, (for_,), IDefaultViewName, '', _context.info,
        ),
    )
