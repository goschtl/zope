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

  AdapterConfigrationAdd

$Id: adapter.py,v 1.3 2002/12/21 15:32:54 poster Exp $
"""
__metaclass__ = type

import md5
from Zope.App.Forms.Utility \
     import setUpWidgets, getWidgetsData, getWidgetsDataForContent, fieldNames
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.interfaces \
     import IAdapterConfiguration, IAdapterConfigurationInfo
from Zope.Event import publish
from Zope.App.Event.ObjectEvent import ObjectCreatedEvent
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfiguration
from Zope.App.OFS.Services.adapter import AdapterConfiguration
from Zope.App.ComponentArchitecture.InterfaceField import InterfaceField
from Interface import Interface
from Zope.ComponentArchitecture import getView
from Zope.Proxy.ContextWrapper import ContextWrapper

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
