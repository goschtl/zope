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

$Id: view.py,v 1.5 2003/06/23 16:20:08 jeremy Exp $
"""

from zope.app.interfaces.services.registration import IRegistration
from zope.app.component.interfacefield import InterfaceField
from zope.app.security.permission import PermissionField
from zope.schema import BytesLine, TextLine, Text, Bool
from zope.interface import Interface
from zope.app.services.field import ComponentPath
from zope.component.interfaces import IPresentation

class ILocalViewService(Interface):
    """Local view service interface.

    Provides an interface for managing and browsing registered views.
    """

    def getRegisteredMatching(required_interfaces=None, presentation_type=None,
                              viewName=None, layer=None):
        """Return registrations matching keyword arg criteria.

        Return is an iterable 5-tuples containing:
        - registered required interface
        - registered provided interface
        - registration stack
        - layer
        - view name
        """


class IAdapterRegistrationInfo(Interface):

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being adapted",
        readonly = True,
        basetype = None
        )

    providedInterface = InterfaceField(
        title = u"Provided interface",
        description = u"The interface provided by the adapter",
        readonly = True,
        required = True,
        )

    adapterName = TextLine(
        title=u"The name of the adapter",
        readonly=True,
        required=False,
        )

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the adapter",
        readonly = True,
        required = True,
        )


class IAdapterRegistration(IRegistration, IAdapterRegistrationInfo):

    def getAdapter(object):
        """Return an adapter for the object

        The adapter is computed by passing the object to the
        registered factory.
        """

class IViewRegistrationInfo(Interface):

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being viewed",
        readonly = True,
        required = True,
        basetype = None
        )

    presentationType = InterfaceField(
        title = u"Presentation type",
        description = u"The presentation type of a view",
        readonly = True,
        required = True,
        basetype = IPresentation,
        constraint = lambda i: i.__name__.endswith("Presentation"),
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

    class_ = BytesLine(
        title=u"View class",
        required = True,
        min_length = 1,
        )

    permission = PermissionField(
        title=u"Permission",
        description=u"The permission required to use the view",
        required = True,
        )


class IViewRegistration(IRegistration, IViewRegistrationInfo):

    def getView(object, request):
        """Return a view for the object

        The view is computed by passing the object to the
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

    expand = Bool(
        title=u"Expand macros",
        )

    def render(context, request, *args, **kw):
        """Render the page template.

        The context argument is bound to the top-level 'context'
        variable.  The request argument is bound to the top-level
        'request' variable. The positional arguments are bound to the
        'args' variable and the keyword arguments are bound to the
        'options' variable.

        """

class IPageRegistrationInfo(IViewRegistrationInfo):

    class_ = BytesLine(
        title=u"Page class",
        required = False,
        )

    template = ComponentPath(
        title = u"Page template",
        required = False,
        type = IZPTTemplate,
        )

    attribute = TextLine(
        title = u"Class attribute",
        required = False,
        )

class IPageRegistration(IRegistration, IPageRegistrationInfo):

    def getView(object, request):
        """Return a page for the object.
        """

    def validate(self):
        """Verifies that the registration is valid.

        Raises a ConfigurationError if the validation is failed.
        """
