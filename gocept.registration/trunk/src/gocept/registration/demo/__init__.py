##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import z3c.formui.interfaces
import z3c.layer.pagelet
import z3c.form.interfaces
import zope.component
import zope.security.management
import gocept.registration.interfaces


class IDemoBrowserLayer(z3c.formui.interfaces.IDivFormLayer,
                        z3c.form.interfaces.IFormLayer,
                        z3c.layer.pagelet.IPageletBrowserLayer):
    """The skin used for demonstration purposes."""


DEMO_TEMPLATE = """From: %(from)s
To: %(to)s
Subject: Please confirm your registration

We received your registration. To activate it, please follow this confirmation
link:

  %(link)s"""


class DemoEmailConfiguration(object):

    zope.component.adapts(gocept.registration.interfaces.IRegistration)
    zope.interface.implements(gocept.registration.interfaces.IEmailConfiguration)

    addr_from = "Ad Ministrator <admin@example.com>"
    confirmation_url = "/confirm.html?hash=%s"
    confirmation_template = DEMO_TEMPLATE

    def __init__(self, registration):
        request = zope.security.management.getInteraction().participations[0]
        self.confirmation_url = (request.getApplicationURL() +
                                 self.confirmation_url)
