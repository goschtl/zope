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

    def getPresentationSkin(self):
        return getattr(self, '_presentation_skin', None)

    def setPresentationSkin(self, skin):
        self._presentation_skin = skin

    HTTPRequest.getPresentationSkin = getPresentationSkin
    HTTPRequest.setPresentationSkin = setPresentationSkin
    HTTPRequest.debug = DebugFlags()

    from RestrictedPython.Utilities import test
    from zope.tales.pythonexpr import PythonExpr

    def __call__(self, econtext):
        __traceback_info__ = self.text
        builtins = __builtins__.copy()
        builtins['test'] = test

        vars = self._bind_used_names(econtext, builtins)
        return eval(self._code, vars)

    PythonExpr.__call__ = __call__

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

class DebugFlags(object):
    """Debugging flags."""

    sourceAnnotations = False
    showTAL = False
