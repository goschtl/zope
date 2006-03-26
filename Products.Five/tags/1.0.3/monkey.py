##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Bad monkey!

$Id$
"""
def monkeyPatch():
    """Trigger all monkey patches needed to make Five work.

    This adjusts Zope 2 classes to make them work with Zope 3.

    Monkey patches are kept to a minimum level.
    """

    from ZPublisher.HTTPRequest import HTTPRequest

    def getPresentationSkin(self):
        return getattr(self, '_presentation_skin', None)

    def setPresentationSkin(self, skin):
        self._presentation_skin = skin

    def getURL(self):
        return self.URL

    HTTPRequest.getPresentationSkin = getPresentationSkin
    HTTPRequest.setPresentationSkin = setPresentationSkin
    HTTPRequest.__contains__ = lambda self, key: self.has_key(key)
    HTTPRequest.getURL = getURL
