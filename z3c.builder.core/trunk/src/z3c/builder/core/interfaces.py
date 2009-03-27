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
"""Builder interfaces

$Id$
"""
import os
import zope.interface
import zope.schema
from zope.container.constraints import contains, containers
from zope.container.interfaces import IOrderedContainer, IContained
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

troveClassifiers = open(os.path.join(os.path.dirname(__file__),
                                     'trove-classifiers.txt')).read().split('\n')
troveClassiferVocabulary = SimpleVocabulary(map(SimpleTerm,
                                                troveClassifiers))

class FileExistsException(Exception):
    """Exception to throw if a file that will be written already exists."""

    filename = None

    def __init__(self, filename, message=u''):
        super(FileExistsException, self).__init__(message)
        self.filename = filename


# --- Basic Builder Components ------------------------------------------------

class IBaseBuilder(IContained):
    """A builder constructs code from a programmatic desciption."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'The name of the builder instance.')

    def update():
        """Update the builder before rendering.

        The purpose of this method is to prepare the builder and dependents
        for rendering.
        """

class IBuilderContainer(IBaseBuilder, IOrderedContainer):
    """A container for other builders."""
    contains(IBaseBuilder)

    def add(builder):
        """Add a builder to the container.

        The name is usually computed from the name of the builder.

        The name of the builder in the component is returned.
        """

    def remove(builder):
        """Remove the builder from the container."""


class IProjectGetter(zope.interface.Interface):
    """Gets the project the builser belongs to."""

    def getProject():
        """Return the project instance."""


class IContentBuilder(IBaseBuilder):
    """Build a piece of content/code within a file."""

    def render():
        """Render the code and return the result as a string."""


class IFilesystemBuilder(IBaseBuilder):
    """Builds and writes a filesystem-level component."""

    def write(target):
        """Write the new file(s) into the target directory."""


class IFileBuilder(IFilesystemBuilder):
    """Bulder to construct a single file with all its content."""

    filename = zope.schema.ASCIILine(
        title=u'File Name',
        description=u'The name of the file to be created.')


class IDirectoryBuilder(IFilesystemBuilder, IBuilderContainer):
    """Builder to construct a directory and all its content."""
    contains(IFileBuilder, '.IDirectoryBuilder')

    dirname = zope.schema.ASCIILine(
        title=u'Directory Name',
        description=u'The name of the directory to be created.')


# --- Python Code Builders ----------------------------------------------------

class IPythonPathRoot(zope.interface.Interface):
    """Marker interface flagging the root directory."""


class IPythonPathGetter(zope.interface.Interface):
    """Gets a full Python path of the current builder."""

    def getPythonPath():
        """Return full Python path as a string."""


class IModuleBuilderGetter(zope.interface.Interface):
    """Gets the next module builder."""

    def getModuleBuilder():
        """Return the next module builder."""


class IPackageBuilder(IDirectoryBuilder, IPythonPathGetter):
    """Builds a full Python package or sub-package."""

    packageName = zope.schema.ASCIILine(
        title=u'Package Name',
        description=u'The name of the package to be created.',
        required=True)

    initTemplate = zope.schema.Bytes(
        title=u'Init Template',
        description=u'The content template for the `__init__.py` file.',
        required=True)


class IModuleBuilder(IFileBuilder, IBuilderContainer, IPythonPathGetter):
    """Builds a Python module."""

    moduleName = zope.schema.ASCIILine(
        title=u'Module Name',
        description=u'The name of the module to be created.')

    imports = zope.schema.List(
        title=u'Import List',
        description=u'The list of objects to import.')


# --- Content Builders --------------------------------------------------------

class IFunctionBuilder(IContentBuilder):
    """A builder to construct a function."""

    args = zope.schema.Tuple(
        title=u'Args',
        description=u'List of function arguments.',
        required=False)

    kwargs = zope.schema.Dict(
        title=u'Kwargs',
        description=u'<apping of function keyword arguments.',
        required=False)

    docstring = zope.schema.ASCII(
        title=u'Interface Docstring',
        description=u'The docstring of the function.')

    indent = zope.schema.Int(
        title=u'Indentation Level',
        description=u'The number of columns to indent the function.',
        default=0)

    code = zope.schema.ASCII(
        title=u'Code',
        description=u'The source code of the function.')


class IFieldBuilder(IContentBuilder):
    """A builder to create a field for an interface builder."""

    fieldName = zope.schema.ASCIILine(
        title=u'Field Name',
        description=u'The name of the field.',
        required=True)

    type = zope.schema.ASCIILine(
        title=u'Type',
        description=u'The full Python path of the type of the field.',
        required=True)

    attributes = zope.schema.Dict(
        title=u'Attributes',
        key_type = zope.schema.ASCIILine(),
        value_type = zope.schema.Field(),
        description=u'The attributes of the field.')

    indent = zope.schema.Int(
        title=u'Indentation Level',
        description=u'The number of columns to indent the field.',
        default=0)


class IInterfaceBuilder(IPythonPathGetter, IContentBuilder):
    """A builder to construct interfaces and schemas."""

    docstring = zope.schema.ASCII(
        title=u'Interface Docstring',
        description=u'The docstring of the itnerface.')

    bases = zope.schema.List(
        title=u'Bases',
        description=u'A list of base interfaces.')


class IClassFromInterfaceBuilder(IContentBuilder):

    #className = zope.schema.TextLine(
    #    title=u'Class Name',
    #    description=u'The name of the generated class.')

    interface = zope.schema.Field(
        title=u'Interface',
        description=u'The interface to generate the class from.')

    docstring = zope.schema.ASCII(
        title=u'Interface Docstring',
        description=u'The docstring of the interface.')

    bases = zope.schema.List(
        title=u'Bases',
        description=u'A list of base interfaces (full Python path).',
        value_type=zope.schema.DottedName(title=u'Full Python Path'))

    implementations = zope.schema.Dict(
        title=u'Implementations',
        description=u'A collection of method implementations.',
        key_type=zope.schema.ASCIILine(),
        value_type=zope.schema.ASCII())


# --- Setup Builders ---------------------------------------------------------

class ISetupBuilder(IFileBuilder):

    version = zope.schema.TextLine(
        title=u"Version",
        default=u"0.1.0",
        required=False)

    license = zope.schema.TextLine(
        title=u"License",
        default=u"GPLv3",
        required=False)

    author = zope.schema.TextLine(
        title=u"Author",
        default=u"",
        required=False)

    author_email = zope.schema.TextLine(
        title=u"Author Email",
        default=u"",
        required=False)

    description = zope.schema.TextLine(
        title=u"Description",
        default=u"",
        required=False)

    keywords = zope.schema.List(
        title=u"Keywords",
        value_type=zope.schema.TextLine(),
        required=False)

    namespace_packages = zope.schema.List(
        title=u'Namespace Packages',
        value_type=zope.schema.TextLine(),
        required=False)

    url = zope.schema.TextLine(
        title=u'URL',
        required=False)

    classifiers = zope.schema.List(
        title=u"Trove Classifiers",
        value_type=zope.schema.Choice(
            vocabulary=troveClassiferVocabulary),
        required=False)

    install_requires = zope.schema.List(
        title=u"Install Requires",
        value_type=zope.schema.ASCIILine(),
        required=False)

    extras_require = zope.schema.Dict(
        title=u"Extras Require",
        key_type=zope.schema.TextLine(),
        value_type=zope.schema.List(value_type=zope.schema.TextLine()))

    entry_points = zope.schema.Dict(
        title=u"Extras Require",
        key_type=zope.schema.TextLine(),
        value_type=zope.schema.List(value_type=zope.schema.TextLine()))

    def addExtrasRequires(name, requirements):
        """Add the requirements to the named extra.

        Multiple calls should not override each other.
        """

    def removeExtrasRequires(name):
        """Remove the requirements from the named extra."""

    def addEntryPoints(name, entries):
        """Add entry points for the given name.

        Multiple calls should not override each other.
        """

    def removeEntryPoints(name):
        """Remove the entry points from the named section."""


# --- Buildout Config Builders ------------------------------------------------

class IPartBuilder(IFileBuilder):

    values = zope.schema.List(
        title=u"Values",
        description=(u"A list of values set for this part."),
        required=True)

    autoBuild = zope.schema.Bool(
        title=u"Auto-Build",
        description=(u"A flag, when set, causes the part to be built "
                     u"automatically"),
        default=True,
        required=True)

    def addValue(key, value):
        """Add a value to the part."""

    def removeValue(key):
        """Remove a value by key."""


class IBuildoutConfigBuilder(IBuilderContainer, IFileBuilder):
    """An object generating the  `buildout.cfg` file."""

    extends = zope.schema.List(
        title=u"Extends",
        description=(u"A list of buildout configurations used to extend the "
                     u"configuration file."),
        value_type=zope.schema.TextLine(),
        required=True)

    names = zope.schema.List(
        title=u"Names",
        description=u"A list of part names that are automatically built.",
        value_type=zope.schema.TextLine(),
        required=True)


# --- ZCML Builders -----------------------------------------------------------

class IZCMLDirectiveBuilder(IBuilderContainer, IContentBuilder):
    """A ZCML Directive Builder."""

    namespace = zope.schema.URI(
        title=u'Namespace',
        description=u'Namespace URI of the directive.',
        required=False)

    #name = zope.schema.TextLine(
    #    title=u'Name',
    #    description=u'The directive name.',
    #    required=True)

    attributes = zope.schema.Dict(
        title=u'Attributes',
        description=u'A collection of attributes of the ZCML directive.',
        required=False)

    indent = zope.schema.Int(
        title=u'Indentation Level',
        description=u'The number of columns to indent the directive.',
        default=0)

    def getZCMLBuilder():
        """Get the ZCML File Builder."""


class IZCMLFileBuilder(IZCMLDirectiveBuilder, IFileBuilder):
    """A ZCML File Builder."""

    i18n_domain = zope.schema.TextLine(
        title=u'I18n Domain',
        description=u'The I18n domain to use for localization.',
        required=False)

    namespaces = zope.schema.List(
        title=u'Namespaces',
        description=u'A list of namespaces used in the file.',
        required=True)


# --- Form Builders -----------------------------------------------------------

class IFormBuilder(IContentBuilder):
    """Generic form builder."""

    interface = zope.schema.ASCIILine(
        title=u'Interface',
        description=u'Full path to the interface.')

    fields = zope.schema.Tuple(
        title=u'Fields',
        description=u'A list of fields to display.',
        value_type=zope.schema.ASCIILine())


class IAddFormBuilder(IFormBuilder):
    """Add form builder."""

    label = zope.schema.TextLine(
        title=u'Label',
        description=u'A label of the form.')

    factory = zope.schema.ASCIILine(
        title=u'Factory',
        description=u'Full path to the factory.')

    next = zope.schema.ASCII(
        title=u'Next URL',
        description=u'The relative URL to go to after adding the object.')


class IEditFormBuilder(IFormBuilder):
    """Edit form builder."""

    label = zope.schema.TextLine(
        title=u'Label',
        description=u'A label of the form.')


class IDisplayFormBuilder(IFormBuilder):
    """Display form builder."""

    template = zope.schema.Text(
        title=u'Template',
        description=u'A template for displaying the data.',
        required=False)


# --- Project Builders --------------------------------------------------------

class IProjectBuilder(IDirectoryBuilder):
    """A Python Project Builder."""

    projectName = zope.schema.ASCIILine(
        title=u"Project Name")

    commentHeader = zope.schema.Text(
        title=u"Comment Header",
        required=False)

    def write(target, force=False):
        """Write the new project in the target directory.

        If `force` is set, then any existing project in the target path is
        ignored, and the new one is wrtten over it.
        """

class IBuildoutProjectBuilder(IProjectBuilder):
    """A Buildout-based Python Project Builder."""

    package = zope.schema.Object(
        title=u"Project Code Package",
        schema=IPackageBuilder,
        readonly=True)

    setup = zope.schema.Object(
        title=u"Project Setup",
        schema=ISetupBuilder,
        readonly=True)

    buildout = zope.schema.Object(
        title=u"Project Buildout",
        schema=IFileBuilder,
        readonly=True)
