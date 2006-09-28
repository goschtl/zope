##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""WebDAV-specific interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface, implements
from zope.schema import Text
from zope.schema.interfaces import IText
from zope.app.form.interfaces import IInputWidget

class IXMLText(IText):
    """A Text field that can optionally contain has its value a
    minidom DOM Node.
    """

class XMLText(Text):
    implements(IXMLText)


class IDAVNamespace(Interface):
    """Represents a namespace available in WebDAV XML documents.

    DAV namespaces and their associated interface are utilities that fullfill
    provide this interface
    """

class IDAVCreationDate(Interface):

    creationdate = Text(
        title=u'''Records the time and date the resource was created''',

        description=u'''The creationdate property should be defined on all
                         DAV compliant resources. If present, it contains a
                         timestamp of the moment when the resource was
                         created (i.e., the moment it had non- null state).''',

        readonly=True)


class IDAVDisplayName(Interface):

    displayname = Text(
        title=u'''Provides a name for the resource that is suitable for\
                  presentation to a user''',

        description=u'''The displayname property should be
                        defined on all DAV compliant
                        resources.  If present, the property
                        contains a description of the resource
                        that is suitable for presentation to a
                        user.''')

class IDAVSource(Interface):

    source = Text(
        title=u'''The destination of the source link\
                  identifies the resource that contains\
                  the unprocessed source of the link\
                  source''',

        description=u'''The source of the link (src) is
                        typically the URI of the output
                        resource on which the link is defined,
                        and there is typically only one
                        destination (dst) of the link, which
                        is the URI where the unprocessed
                        source of the resource may be
                        accessed.  When more than one link
                        destination exists, this specification
                        asserts no policy on ordering.''')


class IOptionalDAVSchema(IDAVCreationDate, IDAVDisplayName, IDAVSource):
    """DAV properties that SHOULD be present but are not required"""


class IGETDependentDAVSchema(Interface):
    """DAV properties that are dependent on GET support of the resource"""

    getcontentlanguage = Text(
        title=u'''Contains the Content-Language\
                  header returned by a GET without\
                  accept headers''',

        description=u'''The getcontentlanguage property MUST
                        be defined on any DAV compliant
                        resource that returns the
                        Content-Language header on a GET.''')

    getcontentlength = Text(
        title=u'''Contains the Content-Length header\
                  returned by a GET without accept\
                  headers''',

        description=u'''The getcontentlength property MUST be
                        defined on any DAV compliant resource
                        that returns the Content-Length header
                        in response to a GET.''',

        readonly=True)

    getcontenttype = Text(
        title=u'''Contains the Content-Type header\
                  returned by a GET without accept\
                  headers''',

        description=u'''This getcontenttype property MUST be
                        defined on any DAV compliant resource
                        that returns the Content-Type header
                        in response to a GET.''')

    getetag = Text(
        title=u'''Contains the ETag header returned by a GET\
                  without accept headers''',

        description=u'''The getetag property MUST be defined
                        on any DAV compliant resource that
                        returns the Etag header.''',

        readonly=True)

    getlastmodified = Text(
        title=u'''Contains the Last-Modified header\
                  returned by a GET method without\
                  accept headers''',

        description=u'''Note that the last-modified date on a
                        resource may reflect changes in any
                        part of the state of the resource, not
                        necessarily just a change to the
                        response to the GET method.  For
                        example, a change in a property may
                        cause the last-modified date to
                        change. The getlastmodified property
                        MUST be defined on any DAV compliant
                        resource that returns the
                        Last-Modified header in response to a
                        GET.''',

        readonly=True)


class IDAV1Schema(IGETDependentDAVSchema):
    """DAV properties required for Level 1 compliance"""

    resourcetype = XMLText(title=u'''Specifies the nature of the resource''',

                           description=u'''
                                The resourcetype property MUST be
                                defined on all DAV compliant
                                resources.  The default value is
                                empty.''',

                           readonly=True)


class IDAV2Schema(IDAV1Schema):
    """DAV properties required for Level 2 compliance"""

    lockdiscovery = Text(
        title=u'''Describes the active locks on a resource''',

        description=u'''The lockdiscovery property returns a
                        listing of who has a lock, what type
                        of lock he has, the timeout type and
                        the time remaining on the timeout,
                        and the associated lock token.  The
                        server is free to withhold any or all
                        of this information if the requesting
                        principal does not have sufficient
                        access rights to see the requested
                        data.''',

        readonly=True)

    supportedlock = Text(
        title=u'''To provide a listing of the lock\
                  capabilities supported by the resource''',

        description=u'''The supportedlock property of a
                        resource returns a listing of the
                        combinations of scope and access types
                        which may be specified in a lock
                        request on the resource.  Note that
                        the actual contents are themselves
                        controlled by access controls so a
                        server is not required to provide
                        information the client is not
                        authorized to see.''',

        readonly=True)

class IDAVSchema(IOptionalDAVSchema, IDAV2Schema):
    """Full DAV properties schema"""


class IDAVWidget(IInputWidget):
    """A specialized widget used to convert to and from DAV properties."""

    def __call__():
        """Render the widget.

        This method should not contain a minidom DOM Node as its value; if its
        value is a minidom DOM Node then its value will be normalized to a
        string.

        If a value should be a minidom DOM Node then use the XMLDAVWidget for
        inserting its value into the DAV XML response.
        """

    def setRenderedValue(value):
        """Set the DAV value for the property
        """


class ITextDAVWidget(IDAVWidget):
    """A DAV widget for text values."""


class ISequenceDAVWidget(IDAVWidget):
    """A DAV widget for sequences."""


class IXMLDAVWidget(IDAVWidget):
    """A DAV widget for rendering XML values.

    This widget should be used if you want to insert any minidom DOM Nodes
    into the DAV XML response.

    It it receives something other then a minidom DOM Node has its value then
    it just renders has an empty string.
    """
