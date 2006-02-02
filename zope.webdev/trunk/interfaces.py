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
"""WebDev Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.i18nmessageid
import zope.schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import zope.app.schema.interfaces
from zope.app import schema
from zope.app.component import interfaces
from zope.app.container import constraints

from zope.app.container.interfaces import IContainer
from zope.app.file.interfaces import IFile

_ = zope.i18nmessageid.MessageFactory('zope.webdev')

class IPackage(interfaces.registration.IRegisterableContainer):
    """A package for the Web-based development

    This object is roughly equivalent to a Python package for filesystem-based
    developement.
    """
    constraints.containers(interfaces.ILocalSiteManager)

    name = zope.schema.BytesLine(
        title=_('Name'),
        description=_('The name of the package, which must be a valid Python '
                      'identifier.'),
        required=True,
        # The name is usually controlled by the containment variable.
        readonly=True)

    docstring = zope.schema.Text(
        title=_('Docstring'),
        description=_('The documentation string for the package.'),
        required=False)

    version = zope.schema.TextLine(
        title=_('Version'),
        description=_('The version of the package.'),
        required=False)

    license = zope.schema.TextLine(
        title=_('License'),
        description=_('The source code license of the package.'),
        required=False)

    author = zope.schema.TextLine(
        title=_('Author'),
        description=_('The author of the package.'),
        required=False)


class ISchema(schema.interfaces.IMutableSchema):
    """A schema that can be modified."""

    name = zope.schema.TextLine(
        title=_("Schema Name"),
        description=_("This is the name of the schema."),
        required=True,
        readonly=True)

    docstring = zope.schema.Text(
        title=_('Docstring'),
        description=_('The documentation string for the schema.'),
        required=False)

    bases = zope.schema.List(
        title=_('Bases'),
        description=_("Specifies the bases for the schema."),
        value_type=zope.schema.Choice(vocabulary='Interfaces'),
        required=True)


class IContentComponentDefinition(interfaces.ILocalUtility):
    """Content Component Definitions describe simple single-schema based
    content components including their security declarations."""
    constraints.containers(IPackage)

    name = zope.schema.TextLine(
        title=_("Content Type Name"),
        description=_("This is the name of the content component type."),
        required=True,
        readonly=True)

    schema = zope.schema.Choice(
        title=_('Schema'),
        description=_("Specifies the schema that characterizes the component."),
        vocabulary="Interfaces",
        required=True)

    permissions = zope.interface.Attribute(
        u"A dictionary that maps set/get permissions on the schema's"
        u"fields. Entries looks as follows: {fieldname:(set_perm, get_perm)}")

    def __call__(**kwargs):
        """Constructor for the content component instance.

        The keyword arguments will be used to set the attributes on the
        instance.
        """


class IContentComponentInstance(zope.interface.Interface):
    """Interface describing a Content Component Instance"""

    __definition__ = zope.schema.Object(
        title=_("Content Component Definition"),
        description=_("The content component definition for which the "
                      "instance is created."),
        schema=IContentComponentDefinition,
        required=True)

    def update():
        """Update the content component instance to the latest definition.

        This method is useful during development. If you keep changing the
        schema and permissions of the content component definition, this
        method can update the instance to apply the changes.
        """

class IPage(interfaces.registration.IRegisterable):
    """A persistent page."""

    name = zope.schema.TextLine(
        title=_("Page Name"),
        description=_("This is the name of the page."),
        required=True,
        readonly=True)

    for_ = zope.schema.Choice(
        title=_('For'),
        description=_("The interface the page is for."),
        vocabulary="Interfaces",
        required=True)

    layers = zope.schema.List(
        title=_('Layers'),
        description=_("The layers in which the page will be available."),
        required=True,
        default=[IDefaultBrowserLayer],
        value_type=zope.schema.Choice(
            vocabulary="Layers",
            )
        )

    permission = zope.schema.Choice(
        title=_(u"Permission"),
        description=_(u"The permission required to view the page"),
        vocabulary="Permission Ids",
        required = True,
        )

    templateSource = zope.schema.Text(
        title=_("Template Source"),
        description=_("The page template source of the template."),
        required=True,
        default=u'')

    moduleSource = zope.schema.Text(
        title=_("Module Source"),
        description=_("The Python source that provides the view class."),
        required=True,
        default=u'')

    className = zope.schema.BytesLine(
        title=_("Class Name"),
        description=_("The name of the class defined in the module."),
        required=True)

    def getTemplate():

        """returns the template"""

class IResourceContainer(IContainer,
                         interfaces.registration.IRegisterable):
    """An interface for a resource container
    """
    constraints.contains(IFile)
    
    name = zope.schema.TextLine(
        title=_("Name"),
        description=_("This is the name of the page."),
        required=True,
        readonly=True)

    permission = zope.schema.Choice(
        title=_(u"Permission"),
        description=_(u"The permission required to view resources"),
        vocabulary="Permission Ids",
        required = True,
        )

    layers = zope.schema.List(
        title=_('Layers'),
        description=_("The layers in which the resources will be available."),
        required=True,
        default=[IDefaultBrowserLayer],
        value_type=zope.schema.Choice(
            vocabulary="Layers",
            )
        )
