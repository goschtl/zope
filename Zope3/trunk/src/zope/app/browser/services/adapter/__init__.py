##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Views for local adapter registration.

  AdapterSeviceView -- it's a bit different from other services, as it
  has a lot of things in it, so we provide a search interface:

    search page
    browsing page

  AdapterRegistrationAdd

$Id: __init__.py,v 1.2 2003/11/21 17:11:11 jim Exp $
"""
__metaclass__ = type

from zope.app.form.utility import setUpWidgets, getWidgetsData


import md5

from zope.interface import Interface
from zope.schema import getFieldNamesInOrder
from zope.component import getView
from zope.publisher.browser import BrowserView

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.services.adapter import IAdapterRegistration
from zope.app.interfaces.services.registration import IRegistration
from zope.app.form.utility import getWidgetsDataForContent
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.services.adapter import AdapterRegistration
from zope.app.component.interfacefield import InterfaceField

class AdapterRegistrationAdd(BrowserView):

    def __init__(self, *args):
        super(AdapterRegistrationAdd, self).__init__(*args)
        setUpWidgets(self, IAdapterRegistration)

    def refresh(self):
        if "FINISH" in self.request:
            data = getWidgetsData(self, IAdapterRegistration, strict=True)
            registration = AdapterRegistration(**data)
            publish(self.context.context, ObjectCreatedEvent(registration))
            registration = self.context.add(registration)
            getWidgetsDataForContent(self, IRegistration, registration,
                                     strict=False)
            self.request.response.redirect(self.context.nextURL())
            return False

        return True

    def getWidgets(self):
        return ([getattr(self, name)
                 for name in getFieldNamesInOrder(IAdapterRegistration)]
                +
                [getattr(self, name)
                 for name in getFieldNamesInOrder(IRegistration)]
                )
