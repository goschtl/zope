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
        from Products.Five.bbb import transaction
        sys.modules['transaction'] = transaction
 
    from Acquisition import aq_inner, aq_parent
    from zope.app.site.interfaces import ISiteManager
    from zope.component.exceptions import ComponentLookupError

    def getLocalServices(context):
        """Returns the service manager that contains `context`.

        If `context` is a local service, returns the service manager
        that contains that service. If `context` is a service manager,
        returns `context`.

        Otherwise, raises ``ComponentLookupError('Services')``

        XXX Basically, this overrides the one in Zope3 X3.0 so that it
        uses acquisition instead of looking up __parent__.
        """

        # IMPORTANT
        #
        # This is not allowed to use any services to get its job done!

        while not (context is None or
                   ISiteManager.providedBy(context)):
            context = aq_parent(aq_inner(context))
        if context is None:
            raise ComponentLookupError('Services')
        else:
            return context

    from zope.app.component import localservice
    localservice.getLocalServices = getLocalServices

