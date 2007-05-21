##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "ReStructuredText"

import zope.interface
import zope.schema
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.interfaces import IContainer
from zope.app.container.constraints import containers
from zope.app.container.constraints import contains
from zope.app.component.interfaces import IPossibleSite
from zope.app.file.interfaces import IFile as ZIFile
from zope.app.file.interfaces import IImage as ZIImage
from zope.app.session.interfaces import ISession
from z3c.resource.interfaces import IResourceTraversable
from z3c.resource.interfaces import IResourceItem
from z3c.website.i18n import MessageFactory as _


class IContent(IResourceTraversable):
    """Page interface."""

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title of the html page.'),
        default=u'',
        missing_value=u'',
        required=False)

    description = zope.schema.Text(
        title=_(u'Description'),
        description=_(u'Description of the content.'),
        default=u'',
        missing_value=u'',
        required=False)

    keyword = zope.schema.Text(
        title=_(u'Keyword'),
        description=_(u'Keyword of the content.'),
        default=u'',
        missing_value=u'',
        required=False)

    body = zope.schema.Text(
        title=_(u'Body'),
        description=_(u'Body is the main part of the page.'),
        default=u'',
        missing_value=u'',
        required=False)


class IWebSite(IContent, IPossibleSite):
    """JQuery demo site."""

    containers('zope.app.filder.interfaces.IFolder')
    contains('z3c.website.interfaces.IPage', 
             'z3c.website.interfaces.ISamples')

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the site.'),
        default=u"Zope3 and JQuery",
        required=True)


class IPage(IContainer, IContent):
    """Page interface."""

    containers('z3c.website.interfaces.IWebSite', 
               'z3c.website.interfaces.IPage')
    contains('z3c.website.interfaces.IPage')


class ISamples(IPage):
    """Container for samples"""

    containers(IWebSite)
    contains('z3c.website.interfaces.ISample')

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("The application title."),
        required=True)


class ISample(IContent):
    """Base class for Z3C sample objects."""

    containers(ISamples)


class ISessionData(zope.interface.Interface):
    """Simple data object which offers a field called content."""

    content = zope.schema.Text(
        title=u'Content',
        description=u'The content field',
        default=u'')


class IDemoSession(ISession):
    """Simply session which knows how to set and get a object."""

    def setObject(key, obj):
        """Add a object to the session."""

    def getObject(key, default=None):
        """Get a object from the session."""


class IFile(IResourceItem, ZIFile):
    """File resource item."""


class IImage(IResourceItem, ZIImage):
    """Image resource item."""
