##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""'dav' ZCML namespace schemas

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.configuration.fields import GlobalInterface
from zope.interface import Interface
from zope.schema import URI, TextLine

class IProvideInterfaceDirective(Interface):
    """This directive assigns a new interface to a component. This interface
    will be available via WebDAV for this particular component."""

    for_ = URI(
        title=u"Namespace",
        description=u"Namespace under which this interface will be available"\
                    u" via DAV.",
        required=True)

    interface = GlobalInterface(
        title=u"Interface",
        description=u"Specifies an interface/schema for DAV.",
        required=True)

#
# new WebDAV configuration.
#

from zope.configuration.fields import Tokens
from zope.configuration.fields import GlobalObject
from zope.configuration.fields import GlobalInterface


class IBaseSchemaDirective(Interface):

    namespace = URI(
        title = u'Namespace',
        description = u'Namespace under which this interface will be available'\
                      u' via DAV.',
        required = True)

    restricted_properties = Tokens(
        title = u'Restricted Properties',
        description = u'A list of property names that should not be rendered' \
                      u' has part of the allprop PROPFIND request',
        required = False,
        value_type = TextLine())

class ISchemaDirective(IBaseSchemaDirective):
    """Register a schema for a specified namespace
    """

    schemas = Tokens(
        title = u'Schemas',
        description = u'List of specific schema containing all the' \
                      u' properties to display',
        required = True,
        value_type = GlobalInterface())


class INamespaceDirective(IBaseSchemaDirective):
    """Registration new namespace with Zope.
    """

    schemas = Tokens(
        title = u'Schemas',
        description = u'List of specific schema containing all the' \
                      u' properties to display',
        required = False,
        value_type = GlobalInterface())

    interfaceType = GlobalInterface(
        title = u'Interface Type',
        description = u'',
        required = False)


class IWidgetSubDirective(Interface):
    """Register Custom WebDAV Widgets for a protocol.
    """

    propname = TextLine(
        title = u'Property Name',
        description = u"""
        The name of the property / field for which this widget will be used.
        """,
        required = True)

    class_ = GlobalObject(
        title = u'WebDAV Widget Class',
        description = u'The class that will create the widget',
        required = True)


class IWidgetDirective(IWidgetSubDirective):
    """Register a custom IDAVWidget widget for a specific property within
    the given namespace.
    """

    namespace = URI(
        title = u'Namespace',
        description = u'Namespace under which this custom widget will be' \
                      u' available.',
        required = True)
