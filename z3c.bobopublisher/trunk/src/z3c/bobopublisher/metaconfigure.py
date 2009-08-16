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



def page(_context, name='index.html', for_=None, class_=None, permission=None,
    methods=None):
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
    for request in requests:
        _context.action(
            discriminator = ('page', for_, name),
            callable = handler,
            args = ('registerAdapter',
                class_, (for_, request), Interface, name, _context.info,
            ),
        )

def resources(_context, name, directory, for_=IRoot, permission=None):
    def resourcesFactory(context, request):
        return Directory(directory)
    if not os.path.isdir(directory):
        raise ConfigurationError('Directory %s does not exist' % directory)
    _context.action(
        discriminator = ('page', for_, name),
        callable = handler,
        args = ('registerAdapter',
            resourcesFactory, (for_, IGETRequest), Interface, name,
            _context.info,
        ),
    )


def resource(_context, name, file, for_=IRoot, permission=None):
    def resourcesFactory(context, request):
        return File(file)
    if not os.path.isfile(file):
        raise ConfigurationError('File %s does not exist' % directory)
    _context.action(
        discriminator = ('page', for_, name),
        callable = handler,
        args = ('registerAdapter',
            resourcesFactory, (for_, IGETRequest), Interface, name,
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
