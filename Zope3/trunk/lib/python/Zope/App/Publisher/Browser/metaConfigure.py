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
"""Browser configuration code

$Id: metaConfigure.py,v 1.5 2002/06/25 14:30:08 mgedmin Exp $
"""

from Zope.Configuration.Action import Action

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation

from Zope.App.ComponentArchitecture.metaConfigure \
     import defaultView as _defaultView, skin as _skin, handler

from ResourceMeta import resource
from I18nResourceMeta import I18nResource
from ViewMeta import view

def skin(_context, **__kw):
    return _skin(_context,
                 type='Zope.Publisher.Browser.IBrowserPresentation.',
                 **__kw)

def defaultView(_context, name, for_=None, **__kw):

    if __kw:
        actions = view(_context, name=name, for_=for_, **__kw)()
    else:
        actions = []

    if for_ is not None:
        for_ = _context.resolve(for_)

    type = IBrowserPresentation

    actions += [Action(
        discriminator = ('defaultViewName', for_, type, name),
        callable = handler,
        args = ('Views','setDefaultViewName', for_, type, name),
        )]

    return actions
