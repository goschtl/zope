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
"""Views for local adapter configuration.

  AdapterSeviceView -- it's a bit different from other services, as it
  has a lot of things in it, so we provide a search interface:

    search page
    browsing page

  AdapterConfigurationAdd

$Id: adapter.py,v 1.3 2002/12/30 14:02:54 stevea Exp $
"""
__metaclass__ = type

import md5
from zope.app.form.utility \
     import setUpWidgets, getWidgetsData, getWidgetsDataForContent, fieldNames
from zope.publisher.browser import BrowserView
from zope.app.interfaces.services.interfaces \
     import IAdapterConfiguration, IAdapterConfigurationInfo
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.interfaces.services.configuration import IConfiguration
from zope.app.services.adapter import AdapterConfiguration
from zope.app.component.interfacefield import InterfaceField
from zope.interface import Interface
from zope.component import getView
from zope.proxy.context import ContextWrapper

class IAdapterSearch(Interface):

    forInterface = InterfaceField(title=u"For interface",
                                  required=False,
                                  )
    providedInterface = InterfaceField(title=u"Provided interface",
                                       required=False,
                                       )


class AdapterServiceView(BrowserView):

    def __init__(self, *args):
        super(AdapterServiceView, self).__init__(*args)
        setUpWidgets(self, IAdapterSearch)

    def configInfo(self):
        forInterface = self.forInterface.getData()
        providedInterface = self.providedInterface.getData()


        result = []
        for (forInterface, providedInterface, registry
             ) in self.context.getRegisteredMatching(forInterface,
                                                     providedInterface):
            forInterface = (
                forInterface.__module__ +"."+ forInterface.__name__)
            providedInterface = (
                providedInterface.__module__ +"."+ providedInterface.__name__)

            registry = ContextWrapper(registry, self.context)
            view = getView(registry, "ChangeConfigurations", self.request)
            prefix = md5.new('%s %s' %
                             (forInterface, providedInterface)).hexdigest()
            view.setPrefix(prefix)
            view.update()
            result.append(
                {'forInterface': forInterface,
                 'providedInterface': providedInterface,
                 'view': view,
                 })

        return result


class AdapterConfigurationAdd(BrowserView):

    def __init__(self, *args):
        super(AdapterConfigurationAdd, self).__init__(*args)
        setUpWidgets(self, IAdapterConfiguration)

    def refresh(self):
        if "FINISH" in self.request:
            data = getWidgetsData(self, IAdapterConfigurationInfo)
            configuration = AdapterConfiguration(**data)
            publish(self.context.context, ObjectCreatedEvent(configuration))
            configuration = self.context.add(configuration)
            getWidgetsDataForContent(self, IConfiguration, configuration)
            self.request.response.redirect(self.context.nextURL())
            return False

        return True

    def getWidgets(self):
        return ([getattr(self, name)
                 for name in fieldNames(IAdapterConfigurationInfo)]
                +
                [getattr(self, name)
                 for name in fieldNames(IConfiguration)]
                )
