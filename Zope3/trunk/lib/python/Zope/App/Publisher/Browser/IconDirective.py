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

$Id: IconDirective.py,v 1.4 2002/12/10 21:41:25 gotcha Exp $
"""
import os
import re

from Zope.App.ComponentArchitecture.metaConfigure import handler
from Zope.Configuration.Action import Action
from Zope.ComponentArchitecture import getResource
from Zope.App.Publisher.Browser import metaConfigure
from Zope.App.Traversing.GetResource import getResource
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.Configuration.Exceptions import ConfigurationError

IName = re.compile('I[A-Z][a-z]')

class IconView:

    def __init__(self, context, request, rname, alt):
        self.context = context
        self.request = request
        self.rname = rname
        self.alt = alt
        
    def __call__(self):
        resource = getResource(self.context, self.rname, self.request)
        src = resource()
        
        return ('<img src="%s" alt="%s" width="16" height="16" border="0" />'
                % (src, self.alt))

    def url(self):
        resource = getResource(self.context, self.rname, self.request)
        src = resource()
        return src

class IconViewFactory:

    def __init__(self, rname, alt):
        self.rname = rname
        self.alt = alt

    def __call__(self, context, request):
        return IconView(context, request, self.rname, self.alt)

def IconDirective(_context, name, for_, file=None, resource=None,
                  layer='default', alt=None):

    for_ = _context.resolve(for_)
    iname = for_.__name__

    if alt is None:
        alt = iname
        if IName.match(alt):
            alt = alt[1:] # Remove leading 'I'

    results = []
    if file is not None and resource is not None:
        raise ConfigurationError(
            "Can't use more than one of file, and resource "
            "attributes for icon directives"
            )
    elif file is not None:
        resource = '-'.join(for_.__module__.split('.'))
        resource = "%s-%s-%s" % (resource, iname, name)
        ext = os.path.splitext(file)[1]
        if ext:
            resource += ext
        results = metaConfigure.resource(_context, image=file,
                              name=resource, layer=layer)()
    elif resource is None:
        raise ConfigurationError(
            "At least one of the file, and resource "
            "attributes for resource directives must be specified"
            )

    vfactory = IconViewFactory(resource, alt)

    return results + [
        Action(
        discriminator = ('view', name, vfactory, layer),
        callable = handler,
        args = ('Views', 'provideView',
                for_, name, IBrowserPresentation,
                vfactory, layer)),
        Action(
        discriminator = None,
        callable = handler,
        args = ('Interfaces', 'provideInterface',
                for_.__module__+'.'+for_.__name__,
                for_)
        )
        ]
