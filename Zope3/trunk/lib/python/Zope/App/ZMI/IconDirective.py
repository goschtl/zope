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

$Id: IconDirective.py,v 1.3 2002/06/13 23:15:44 jim Exp $
"""
import os
import re

from Zope.App.ComponentArchitecture.metaConfigure import handler
from Zope.Configuration.Action import Action
from Zope.ComponentArchitecture import getResource
from Zope.App.Publisher.Browser.metaConfigure import resource
from Zope.App.Traversing.GetResource import getResource
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation

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

class IconViewFactory:

    def __init__(self, rname, alt):
        self.rname = rname
        self.alt = alt

    def __call__(self, context, request):
        return IconView(context, request, self.rname, self.alt)

def IconDirective(_context, for_, file, layer='default',
                  alt=None):

    for_ = _context.resolve(for_)
    iname = for_.__name__

    if alt is None:
        alt = iname    
        if IName.match(alt):
            alt = alt[1:] # Remove leading 'I'

    rname = '-'.join(for_.__module__.split('.'))
    rname = "%s-%s-zmi_icon" % (rname, iname)

    ext = os.path.splitext(file)[1]
    if ext:
        rname += ext
    
    vfactory = IconViewFactory(rname, alt)

    return resource(_context, image=file, name=rname, layer=layer)() + [
        Action(
        discriminator = ('view', 'zmi_icon', vfactory, layer),
        callable = handler,
        args = ('Views', 'provideView',
                for_, 'zmi_icon', IBrowserPresentation,
                vfactory, layer)),
        
        ]
    
    
