##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Bad monkey!

$Id$
"""
def monkeyPatch():
    """Trigger all monkey patches needed to make Five work.

    This adjusts Zope 2 classes to make them work with Zope 3.

    Monkey patches are kept to a minimum level.
    """

    from ZPublisher.HTTPRequest import HTTPRequest

    if not hasattr(HTTPRequest, 'getPresentationSkin'):
        # BBB: for Zope 2.7

        def getPresentationSkin(self):
            return getattr(self, '_presentation_skin', None)

        def setPresentationSkin(self, skin):
            self._presentation_skin = skin

        HTTPRequest.getPresentationSkin = getPresentationSkin
        HTTPRequest.setPresentationSkin = setPresentationSkin

        HTTPRequest.__contains__ = lambda self, key: self.has_key(key)

    from Products.Five import interfaces
    interfaces.monkey()
