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

from zope.component import getGlobalSiteManager
from zope.component.zcml import adapter
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
        adapter(
            _context, (class_,), provides=Interface, for_=(for_, request),
            name=name, permission=permission,
        )

def resources(_context, name, directory, for_=IRoot, permission=None):
    def resourcesFactory(context, request):
        return Directory(directory)
    if not os.path.isdir(directory):
        raise ConfigurationError('Directory %s does not exist' % directory)
    adapter(
        _context, (resourcesFactory,), provides=Interface,
        for_=(for_, IGETRequest), name=name, permission=permission,
    )


def resource(_context, name, file, for_=IRoot, permission=None):
    def resourcesFactory(context, request):
        return File(file)
    if not os.path.isfile(file):
        raise ConfigurationError('File %s does not exist' % directory)
    adapter(
        _context, (resourcesFactory,), provides=Interface,
        for_=(for_, IGETRequest), name=name, permission=permission,
    )


def defaultView(_context, name, for_=None):
    adapter(
        _context, (lambda x: name,), provides=IDefaultViewName, for_=(for_,),
    )
