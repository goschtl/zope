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
"""Service interfaces

$Id: interfaces.py,v 1.2 2002/12/25 14:13:02 jim Exp $
"""

from zope.app.interfaces.services.configuration import IConfiguration
from zope.app.component.interfacefield import InterfaceField
from zope.schema import BytesLine, TextLine, Text
from zope.interface import Interface
from zope.app.services.field import ComponentLocation
from zope.component.interfaces import IPresentation

class IAdapterConfigurationInfo(Interface):

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being adapted",
        readonly = True,
        required = False,  # XXX the UI should be explicit about allowing
        )                  #     no selection.

    providedInterface = InterfaceField(
        title = u"Provided interface",
        description = u"The interface provided by the adapter",
        readonly = True,
        required = True,
        )

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the adapter",
        readonly = True,
        required = True,
        )

class IAdapterConfiguration(IConfiguration, IAdapterConfigurationInfo):

    def getAdapter(object):
        """Return an adapter for the object

        The adapter is computed by passing the object to the
        registered factory.
        """

class IViewConfigurationInfo(Interface):

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being viewed",
        readonly = True,
        required = True,
        )

    presentationType = InterfaceField(
        title = u"Presentation type",
        description = u"The presentation type of a view",
        readonly = True,
        required = True,
        type = IPresentation,
        )

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the view",
        readonly = True,
        required = True,
        min_length = 1,
        )

    viewName = TextLine(
        title = u"View name",
        readonly = True,
        required = True,
        min_length = 1,
        )

    layer = BytesLine(
        title = u"Layer",
        description = u"The skin layer the view is registered for",
        required = False,
        readonly = True,
        min_length = 1,
        default = "default",
        )

class IViewConfiguration(IConfiguration, IViewConfigurationInfo):

    def getView(object, request):
        """Return an adapter for the object

        The adapter is computed by passing the object to the
        registered factory.
        """


class IZPTTemplate(Interface):
    """ZPT Templates for use in views
    """

    contentType = BytesLine(
        title=u'Content type of generated output',
        required=True,
        default='text/html'
        )

    source = Text(
        title=u"Source",
        description=u"""The source of the page template.""",
        required=True)

    def render(context, request, *args, **kw):
        """Render the page template.

        The context argument is bound to the top-level 'context'
        variable.  The request argument is bound to the top-level
        'request' variable. The positional arguments are bound to the
        'args' variable and the keyword arguments are bound to the
        'options' variable.

        """

class IPageConfigurationInfo(IViewConfigurationInfo):

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the view",
        readonly = True,
        required = False,
        min_length = 1,
        )

    template = ComponentLocation(
        title = u"Page template",
        required = False,
        readonly = True,
        type = IZPTTemplate,
        )

class IPageConfiguration(IConfiguration, IPageConfigurationInfo):

    def getView(object, request):
        """Return a page for the object.
        """
