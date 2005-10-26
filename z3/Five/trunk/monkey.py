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

    from Products.Five import interfaces, i18n
    interfaces.monkey()
    i18n.monkey()
    localsites_monkey()

    # XXX in Five 1.3, call this from here:
    if False: # XXX
        from Products.Five import event
        event.doMonkies(transitional=False,
                        info='Five/monkey.py',
                        register_cleanup=False)

def localsites_monkey():
    from Acquisition import aq_inner, aq_parent
    from zope.app.site.interfaces import ISiteManager
    from zope.component.exceptions import ComponentLookupError

    def getLocalServices(context):
        """Returns the service manager that contains `context`.

        If `context` is a local service, returns the service manager
        that contains that service. If `context` is a service manager,
        returns `context`.

        Otherwise, raises ``ComponentLookupError('Services')``

        Basically, this overrides the one in Zope X3 3.0 so that it
        uses acquisition instead of looking up __parent__.  Monkey
        patching Zope 3 sucks, but X3 3.0 leaves us no choice, really.
        Fortunately, this will disappear in Zope 3.2, so we won't wet
        our pants about this now..."""
        # IMPORTANT
        #
        # This is not allowed to use any services to get its job done!

        while not (context is None or
                   ISiteManager.providedBy(context)):
            context = getattr(context, '__parent__', aq_parent(aq_inner(context)))
        if context is None:
            raise ComponentLookupError('Services')
        else:
            return context

    from zope.app.component import localservice
    localservice.getLocalServices = getLocalServices

    from zope.event import notify
    from zope.app.publication.interfaces import EndRequestEvent
    def close(self):
        self.other.clear()
        self._held=None
        notify(EndRequestEvent(None, self))

    from ZPublisher.BaseRequest import BaseRequest
    BaseRequest.close = close
