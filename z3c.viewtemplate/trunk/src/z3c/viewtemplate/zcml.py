##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

import os

from zope import interface
from zope import component
from zope import schema

from zope.component import zcml

from zope.configuration.exceptions import ConfigurationError
import zope.configuration.fields

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.pagetemplate.interfaces import IPageTemplate
from zope.configuration.fields import GlobalObject

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zope')


class ITemplateDirective(interface.Interface):
    """Parameters for the template directive."""

    template = zope.configuration.fields.Path(
            title=_("Content-generating template."),
            description=_("Refers to a file containing a page template (should "
                          "end in extension ``.pt`` or ``.html``)."),
            required=False,
            )

    for_ = GlobalObject(
            title = _(u'View'),
            description = _(u'The view for which the template should be used'),
            required = False,
            default=interface.Interface,
            )

    layer = GlobalObject(
            title = _(u'Layer'),
            description = _(u'The layer for which the template should be used'),
            required = False,
            default=IDefaultBrowserLayer,
            )

    contentType = GlobalObject(
            title = _(u'Content Type'),
            description = _(u'The content type that will be set as part of '
                             'HTTP headers'),
            required = False,
            default='text/html',
            )


class TemplateFactory(object):

    def __init__(self, filename, contentType):
        self.filename = filename
        self.contentType = contentType

    def __call__(self, view, request):
        return ViewPageTemplateFile(self.filename,
                                    content_type=self.contentType)


def templateDirective(_context,
                      template,
                      for_=interface.Interface,
                      layer=IDefaultBrowserLayer,
                      contentType='text/html',
                      ):
    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = TemplateFactory(template, contentType)

    # register the template
    zcml.adapter(_context, (factory,), IPageTemplate, (for_, layer))

