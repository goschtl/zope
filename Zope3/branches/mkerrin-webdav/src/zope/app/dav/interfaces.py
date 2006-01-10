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

from zope.interface import Interface
from zope.schema import Int, Text, TextLine, Dict, Datetime, Date, List, Bool
from zope.schema.interfaces import IText, IList
from zope.app.form.interfaces import IWidget

from fields import IXMLEmptyElementList, XMLEmptyElementList
from fields import IDAVXMLSubProperty, DAVXMLSubProperty, DAVOpaqueField

class IDAVNamespace(Interface):
    """Represents a namespace available in WebDAV XML documents.

    DAV namespaces and their associated interface are utilities that fullfill
    provide this interface
    """


class IDAVCreationDate(Interface):

    creationdate = Datetime(title=u'''Records the time and date the resource\
                                      was created''',

                            description=u'''\
                                      The creationdate property should be
                                      defined on all DAV compliant
                                      resources.  If present, it contains a
                                      timestamp of the moment when the
                                      resource was created (i.e., the moment
                                      it had non- null state).''',

                            readonly = True)


class IDAVDisplayName(Interface):

    displayname = TextLine(title=u'''Provides a name for the resource that\
                                    is suitable for presentation to a\
                                    user''',

                           description=u'''\
                                    The displayname property should be
                                    defined on all DAV compliant
                                    resources.  If present, the property
                                    contains a description of the resource
                                    that is suitable for presentation to a
                                    user.''')

class IDAVSource(Interface):

    source = DAVOpaqueField(title=u'''The destination of the source link\
                                      identifies the resource that contains\
                                      the unprocessed source of the link\
                                      source''',

                            description=u'''\
                                      The source of the link (src) is
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

    getcontentlanguage = TextLine(title=u'''Contains the Content-Language\
                                            header returned by a GET without\
                                            accept headers''',

                                  description=u'''\
                                         The getcontentlanguage property MUST
                                         be defined on any DAV compliant
                                         resource that returns the
                                         Content-Language header on a GET.''')

    getcontentlength = Int(title=u'''Contains the Content-Length header\
                                     returned by a GET without accept\
                                     headers''',

                           description=u'''\
                                The getcontentlength property MUST be
                                defined on any DAV compliant resource
                                that returns the Content-Length header
                                in response to a GET.''',

                           readonly = True)

    getcontenttype = TextLine(title=u'''Contains the Content-Type header\
                                        returned by a GET without accept\
                                        headers''',

                              description=u'''\
                                    This getcontenttype property MUST be
                                    defined on any DAV compliant resource
                                    that returns the Content-Type header
                                    in response to a GET.''')

    getetag = TextLine(title=u'''Contains the ETag header returned by a GET\
                                 without accept headers''',

                       description=u'''\
                                 The getetag property MUST be defined
                                 on any DAV compliant resource that
                                 returns the Etag header.''',

                       readonly = True)

    getlastmodified = Datetime(title=u'''Contains the Last-Modified header\
                                         returned by a GET method without\
                                         accept headers''',

                               description=u'''\
                                      Note that the last-modified date on a
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

                               readonly = True)


class IDAVResourceSchema(Interface):
    """DAV properties required for Level 1 compliance"""

    resourcetype = XMLEmptyElementList(
                           title = u'''Specifies the nature of the resource''',

                           description = u'''\
                                 The resourcetype property MUST be
                                 defined on all DAV compliant
                                 resources.  The default value is
                                 empty.''',

                           readonly = True,

                           value_type = TextLine(title = u'resource type')
                           )

class IDAVLockEntry(Interface):
    """A DAV Sub property of the supportedlock property.
    """
    lockscope = XMLEmptyElementList(title = u'''\
                            Describes the exclusivity of a lock''',

                                    description = u'''\
                            Specifies whether a lock is an exclusive lock, or a
                            shared lock.''',

                                    readonly = True,

                                    value_type = TextLine(title = u''))

    locktype = XMLEmptyElementList(title = u'''\
                            Describes the access type of the lock''',

                                   description = u'''\
                            Specifies the access type of a lock. At present,
                            this specification only defines one lock type, the
                            write lock.''',

                                   readonly = True,

                                   value_type = TextLine(title = u''))


class IDAVActiveLock(Interface):
    """A DAV Sub property of the lockdiscovery property.
    """
    lockscope = XMLEmptyElementList(title = u'''\
                            Describes the exclusivity of a lock''',

                                    description = u'''\
                            Specifies whether a lock is an exclusive lock, or a
                            shared lock.''',

                                    value_type = TextLine(title = u''))

    locktype = XMLEmptyElementList(title = u'''\
                            Describes the access type of the lock''',

                                   description = u'''\
                            Specifies the access type of a lock. At present,
                            this specification only defines one lock type, the
                            write lock.''',

                                   value_type = TextLine(title = u''))

    depth = Text(title = u'Depth',
                 description = u'The value of the Depth header.')

    ## this is the wrong field. After reading RFC3744 extra semantics are
    ## supplied to this field. Further research into this and other RFC3744
    ## properties is required.
    owner = DAVOpaqueField(title = u'Owner',
                           description = u'''\
                        The owner XML element provides information sufficient
                        for either directly contacting a principal (such as a
                        telephone number or Email URI), or for discovering the
                        principal (such as the URL of a homepage) who owns a
                        lock.''')

    timeout = Text(title = u'Timeout',
                   description = u'The timeout associated with a lock')

    locktoken = DAVOpaqueField(title = u'Lock Token',
                               description = u'''\
                           The href contains one or more opaque lock token URIs
                           which all refer to the same lock (i.e., the
                           OpaqueLockToken-URI production in section 6.4).''')


class IDAVLockSchema(Interface):
    """DAV properties required for Level 2 compliance"""

    lockdiscovery = DAVXMLSubProperty(title=u'''Describes the active locks on a\
                                                resource''',

                                      description=u'''\
                                         The lockdiscovery property returns a
                                         listing of who has a lock, what type
                                         of lock he has, the timeout type and
                                         the time remaining on the timeout,
                                         and the associated lock token.  The
                                         server is free to withhold any or all
                                         of this information if the requesting
                                         principal does not have sufficient
                                         access rights to see the requested
                                         data.''',

                                      readonly = True,

                                      prop_name = 'activelock',

                                      schema = IDAVActiveLock)

    supportedlock = DAVXMLSubProperty(title = u'''\
                                           To provide a listing of the lock\
                                           capabilities supported by the\
                                           resource''',

                                      description=u'''\
                                The supportedlock property of a
                                resource returns a listing of the
                                combinations of scope and access types
                                which may be specified in a lock
                                request on the resource.  Note that
                                the actual contents are themselves
                                controlled by access controls so a
                                server is not required to provide
                                information the client is not
                                authorized to see.''',

                                      readonly = True,

                                      schema = IDAVLockEntry,

                                      prop_name = 'lockentry')

class IDAVCollectionSchema(IOptionalDAVSchema, IDAVLockSchema,
                           IDAVResourceSchema):
    """DAV properties schema that applies to a collection.

    Not that all the get* properties don't apply to collections.
    """


class IDAVSchema(IOptionalDAVSchema, IGETDependentDAVSchema, IDAVLockSchema,
                 IDAVResourceSchema):
    """Full DAV properties schema"""


class IDAVWidget(IWidget):
    """A specialized widget used to convert to and from DAV properties."""

    required = Bool(
        title=u"Required",
        description=u"""If True, widget should be displayed as requiring input.

        By default, this value is the field's 'required' attribute. This
        field can be set to False for widgets that always provide input (e.g.
        a checkbox) to avoid unnecessary 'required' UI notations.
        """)

    def getInputValue():
        """Return value suitable for the widget's field.

        The widget must return a value that can be legally assigned to
        its bound field or otherwise raise ``WidgetInputError``.

        The return value is not affected by `setRenderedValue()`.
        """

    def applyChanges(content):
        """Validate the user input data and apply it to the content.

        Return a boolean indicating whether a change was actually applied.

        This raises an error if there is no user input.
        """

    def hasInput():
        """Returns ``True`` if the widget has input.

        Input is used by the widget to calculate an 'input value', which is
        a value that can be legally assigned to a field.

        Note that the widget may return ``True``, indicating it has input, but
        still be unable to return a value from `getInputValue`. Use
        `hasValidInput` to determine whether or not `getInputValue` will return
        a valid value.

        A widget that does not have input should generally not be used
        to update its bound field.  Values set using
        `setRenderedValue()` do not count as user input.

        A widget that has been rendered into a form which has been
        submitted must report that it has input.  If the form
        containing the widget has not been submitted, the widget
        shall report that it has no input.

        """

    def hasValidInput():
        """Returns ``True`` is the widget has valid input.

        This method is similar to `hasInput` but it also confirms that the
        input provided by the user can be converted to a valid field value
        based on the field constraints.
        """

    def setRenderedValue(value):
        """Set the value of the field associated with this widget.

        This value must validate to the type expected by the associated field.
        """

    def setProperty(propel):
        """Parse the DOM element ``propel`` and store the extracted value in
        the widget.

        The extracted value must validate against the associated field.
        """

    def renderProperty(ns, ns_prefix):
        """Render a property has a DOM elements.
        """

##     def removeProperty(self, ns, prop):
##         """
##         """


class IIfHeader(Interface):
    """RFC 2518 Section ...
    """

    def __call__():
        """Return True / False wheather the current context and request
        matches the the IF HTTP header has specified in RFC 2518
        """
