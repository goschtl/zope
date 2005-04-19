##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Provide basic browser functionality

$Id$
"""
import Acquisition
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class BrowserView(Acquisition.Explicit):
    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # XXX do not create any methods on the subclass called index_html,
    # as this makes Zope 2 traverse into that first!

InitializeClass(BrowserView)
