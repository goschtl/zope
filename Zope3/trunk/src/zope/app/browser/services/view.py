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
"""Views for local view configuration.

  ViewSeviceView -- it's a bit different from other services, as it
  has a lot of things in it, so we provide a search interface:

    search page
    browsing page

  PageConfigurationView -- calls validation on PageConfiguration.

$Id: view.py,v 1.8 2003/04/11 19:05:08 fdrake Exp $
"""
__metaclass__ = type

import md5

from zope.interface import Interface
from zope.schema import TextLine, BytesLine
from zope.component.interfaces import IPresentation
from zope.component import getView
from zope.proxy.context import ContextWrapper
from zope.publisher.browser import BrowserView

from zope.app.form.utility import setUpWidgets
from zope.app.component.interfacefield import InterfaceField
# XXX These are not used in this module, but are referenced in configure.zcml.
#  either configure.zcml should be fixed, or a comment should replace
#  this one to explain why configure.zcml is importing these two names
#  from here rather than from where they are defined.
from zope.app.services.view import ViewConfiguration, PageConfiguration

class IViewSearch(Interface):

    forInterface = InterfaceField(title=u"For interface",
                                  required=False,
                                  )
    presentationType = InterfaceField(title=u"Provided interface",
                                      required=False,
                                      basetype=IPresentation
                                      )

    viewName = TextLine(title=u'View name',
                        required=False,
                        )

    layer = BytesLine(title=u'Layer',
                      required=False,
                      )


class ViewServiceView(BrowserView):

    def __init__(self, *args):
        super(ViewServiceView, self).__init__(*args)
        setUpWidgets(self, IViewSearch)

    def configInfo(self):
        input_for = self.forInterface.getData()
        input_type = self.presentationType.getData()
        input_name = self.viewName.getData()
        input_layer = self.layer.getData()

        result = []
        for info in self.context.getRegisteredMatching(
            input_for, input_type, input_name, input_layer):

            forInterface, presentationType, registry, layer, viewName = info

            forInterface = (
                forInterface.__module__ +"."+ forInterface.__name__)
            presentationType = (
                presentationType.__module__ +"."+ presentationType.__name__)

            registry = ContextWrapper(registry, self.context)
            view = getView(registry, "ChangeConfigurations", self.request)
            prefix = md5.new('%s %s' %
                             (forInterface, presentationType)).hexdigest()
            view.setPrefix(prefix)
            view.update()

            if input_name is not None:
                viewName = None

            if input_layer is not None:
                layer = None

            result.append(
                {'forInterface': forInterface,
                 'presentationType': presentationType,
                 'view': view,
                 'viewName': viewName,
                 'layer': layer,
                 })

        return result

class PageConfigurationView:

    def update(self):
        super(PageConfigurationView, self).update()
        if "UPDATE_SUBMIT" in self.request:
            self.context.validate()
