##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Presentation interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

import zope.app.container
import zope.app.component.interfaces
from zope.app.container import constraints
from zope.app.i18n import ZopeMessageIDFactory as _


class IPageRegistration(zope.app.component.interfaces.IAdapterRegistration):

    requestType = zope.schema.Choice(
        title = _(u"Request type"),
        description = _(u"The type of requests the view works with"),
        vocabulary="Interfaces",
        readonly = True,
        required = True,
        )

    template = zope.app.component.interfaces.registration.Component(
        title = _(u"Page template"),
        required = False,
        )

    attribute = zope.schema.TextLine(
        title = _(u"Class attribute"),
        required = False,
        )

    def validate(self):
        """Verifies that the registration is valid.

        Raises a ConfigurationError if the validation is failed.
        """

class IZPTInfo(zope.interface.Interface):
    """ZPT Template configuration information
    """

    contentType = zope.schema.BytesLine(
        title=u'Content type of generated output',
        required=True,
        default='text/html'
        )

    source = zope.schema.Text(
        title=u"Source",
        description=u"""The source of the page template.""",
        required=True)

    expand = zope.schema.Bool(
        title=u"Expand macros",
        )


class IZPTTemplate(IZPTInfo,
                   zope.app.component.interfaces.registration.IRegisterable):
    """ZPT Templates for use in views"""

    def render(context, request, *args, **kw):
        """Render the page template.

        The context argument is bound to the top-level `context`
        variable.  The request argument is bound to the top-level
        `request` variable. The positional arguments are bound to the
        `args` variable and the keyword arguments are bound to the
        `options` variable.

        """


class IPageFolderInfo(zope.interface.Interface):
    """Default registration information for page folders

    This information is used to configure the pages in the folder.
    """

    required = zope.schema.Choice(
        title = _(u"For interface"),
        description = _(u"The interface of the objects being viewed"),
        vocabulary="Interfaces",
        required = True,
        )

    factoryName = zope.schema.BytesLine(
        title=_(u"The dotted name of a factory for creating the view"),
        required = False,
        )
    permission = zope.schema.Choice(
        title=_(u"Permission"),
        description=_(u"The permission required to use the view"),
        vocabulary="Permission Ids",
        required = True,
        )

    apply = zope.schema.Bool(
        title=_(u"Apply changes to existing pages"),
        required = True,
        )


class IPageFolder(
    IPageFolderInfo,
    zope.app.container.interfaces.IContainer,
    zope.app.component.interfaces.registration.IRegisterableContainer):

    constraints.contains(IZPTTemplate)
    constraints.containers(
        zope.app.component.interfaces.registration.IRegisterableContainer)

    def applyDefaults(self):
        """Apply the default configuration to the already-registered pages. 
        """
