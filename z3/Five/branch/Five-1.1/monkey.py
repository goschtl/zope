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

    if not hasattr(HTTPRequest, 'getPresentationSkin'):
        # BBB: for Zope 2.7

        def getPresentationSkin(self):
            return getattr(self, '_presentation_skin', None)

        def setPresentationSkin(self, skin):
            self._presentation_skin = skin

        HTTPRequest.getPresentationSkin = getPresentationSkin
        HTTPRequest.setPresentationSkin = setPresentationSkin

        HTTPRequest.__contains__ = lambda self, key: self.has_key(key)

    if not hasattr(HTTPRequest, 'getURL'):
        # BBB: for Zope 2.7, 2.8.0
        def getURL(self):
            return self.URL
        HTTPRequest.getURL = getURL

    from Products.Five import interfaces, i18n
    interfaces.monkey()
    i18n.monkey()

    try:
        import Zope2
    except ImportError:
        import sys
        import transaction
        from Products.Five.bbb import transaction_patch
        transaction.begin = transaction_patch.begin
        transaction.commit = transaction_patch.commit
        transaction.abort = transaction_patch.abort
        transaction.get_transaction = transaction_patch.get_transaction
        transaction.get = transaction_patch.get
