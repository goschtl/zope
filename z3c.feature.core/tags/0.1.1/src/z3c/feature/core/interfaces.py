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
"""Feature interfaces

$Id$
"""
import datetime
import os

import zope.interface
from zope.interface.interfaces import IInterface
import zope.schema

from z3c.builder.core.interfaces import troveClassiferVocabulary

FEATURE_GROUP = 'z3c.feature'

class IFeatureType(IInterface):
    """An interface that describes a particular type of feature."""

class DuplicateFeatureConflictError(ValueError):

    def __init__(self, type):
        self.type = type
        ValueError.__init__(self, type)

class CyclicDependencyError(ValueError):

    def __init__(self, cycle):
        self.cycle = cycle
        ValueError.__init__(self, cycle)

class MissingFeatureDependencyError(KeyError):
    def __init__(self, feature, dependencyName):
        self.feature = feature
        self.dependencyName = dependencyName
        KeyError.__init__(self, dependencyName)

    def __str__(self):
        return ('Feature "%s" depends on "%s" but no "%s" '
                'feature was specified') % (self.feature.featureTitle,
                                            self.dependencyName,
                                            self.dependencyName)

class IFeatureSchema(IInterface):
    """A schema describing the configuration parameters of a feature."""

class IBaseFeatureSchema(zope.interface.Interface):
    """A trivial feature schema."""
zope.interface.directlyProvides(IBaseFeatureSchema, IFeatureSchema)


class IFeature(zope.interface.Interface):
    """An object representing a possible feature."""

    featureTitle = zope.schema.TextLine(
        title=u"Feature Title",
        description=u"A user readable title for this feature.")

    featureDocumentation = zope.schema.Text(
        title=u"Feature Documentation",
        description=u"""ReSTructured text documentation on the feature.

        This should explain what files were modified/created by the
        feature and what each piece does, with tips on modifying them
        later.  Documentation for all the features are combined into
        a single README.txt in the project Root.
        """)

    featureSingleton = zope.schema.Bool(
        title=u"Feature Sigelton",
        description=(u"When set, only one instance of this feature can "
                     u"be applied to the context."),
        default=True)

    featureDependencies = zope.schema.Tuple(
        title=u"Feature Dependencies",
        description=(u"A list of names of features that this feature "
                     u"depends on."),
        value_type=zope.schema.ASCIILine())

    def update(features=()):
        """Update the feature.

        Optionally, all other features that are applied are passed into the
        method as an argument.
        """

    def applyTo(context):
        """Apply the given feature to the context."""

    def findEntryPoint():
        """Returns the egg name and entry point name.

        If no entry point is found, `(None, None)` is returned.
        """

    def toXML(asString=False, prettyPrint=False):
        """Returns an etree node object representing the feature in xml.

        Optional keyword arguments include asString and prettyPrint
        which if set to true will return an xml string that is pretty
        printed.
        """

class IHaveAppliedFeatures(zope.interface.Interface):
    """A component that keeps track of the features applied to it."""

    appliedFeatures = zope.schema.List(
        title=u'Applied Features',
        description=u'A list of features that were applied on the builder.')


class IProjectTemplateProvider(zope.interface.Interface):
    """Object that provides a projecte template."""

    title = zope.schema.TextLine(
        title=u"Title",
        description=u"A title that can be provided to the user.")

    description = zope.schema.TextLine(
        title=u"Description",
        description=u"A description that can be provided to the user.")

    def getFeatures():
        """Returns a dictionary of entrypoint name to features that
           are part of this template."""


class IFileBasedTemplateProvider(IProjectTemplateProvider):

    filename = zope.schema.TextLine(
        title=u"Filename")


class IMetaDataFeature(zope.interface.Interface):

    license = zope.schema.TextLine(
        title=u'License',
        default=u'GNU General Public License (GPL)',
        required=False)

    version = zope.schema.TextLine(
        title=u'Version',
        description=u'An initial version number for the project',
        default=u'0.1.0',
        required=False)

    description = zope.schema.TextLine(
        title=u'Project Description',
        description=u'Short Description of the project',
        required=False)

    author = zope.schema.TextLine(
        title=u'Author(s)',
        description=u'Name of the project author(s)',
        required=False)

    author_email = zope.schema.TextLine(
        title=u'Author Email',
        description=u'Email address for the project author(s)',
        required=False)

    keywords = zope.schema.List(
        title=u'Keywords',
        description=u'A list of keywords related to the project, one per line.',
        value_type=zope.schema.TextLine(),
        required=False)

    url = zope.schema.TextLine(
        title=u'URL',
        description=(u'The url for the project. Defaults to '
                     u'http://pypi.python.org/pypi/[project-name]'),
        required=False)

    classifiers = zope.schema.Set(
        title=u"Trove Classifiers",
        value_type=zope.schema.Choice(
            vocabulary=troveClassiferVocabulary),
        required=False)

    commentHeader = zope.schema.Text(
        title=u'Comment Header',
        description=(u'A comment header that should appear at the top of every '
                     u'python file (like a license header).'),
        required=False)

    namespace_packages = zope.schema.List(
        title=u'Namespace Packages',
        description=(u'A list of namespace packages that should be created, one '
                     u'per line (i.e. zope or zc or z3c or collective)'),
        value_type=zope.schema.TextLine(),
        required=False)

    install_requires = zope.schema.List(
        title=u"Install Requires",
        description=(u"A list of additional dependencies, one per line "
                     u"(i.e. lxml)"),
        value_type=zope.schema.TextLine(),
        required=False)

    extras_require = zope.schema.Dict(
        title=u"Extras Require",
        key_type=zope.schema.TextLine(),
        value_type=zope.schema.List(value_type=zope.schema.TextLine()))

zope.interface.directlyProvides(IMetaDataFeature, IFeatureSchema)


class ICommentHeaderZPLFeature(zope.interface.Interface):

    author = zope.schema.TextLine(
        title=u'Author(s)',
        description=u'Name of the project author(s)',
        required=False)

    year = zope.schema.Int(
        title=u"Year",
        description=u'The copyright year',
        default=datetime.date.today().year)

zope.interface.directlyProvides(ICommentHeaderZPLFeature, IFeatureSchema)


class IProprietaryHeaderFeature(zope.interface.Interface):

    year = zope.schema.Int(
        title=u"Year",
        description=u'The copyright year',
        default=datetime.date.today().year)

    company = zope.schema.TextLine(
        title=u'Company',
        description=u'The name of your company, (i.e. Foo Inc.)')

    location = zope.schema.TextLine(
        title=u'Location',
        description=u'Location of your company (i.e. San Francisco, USA)')

zope.interface.directlyProvides(IProprietaryHeaderFeature, IFeatureSchema)


class IPythonInterpreterFeature(zope.interface.Interface):

    executableName = zope.schema.ASCIILine(
        title=u'Executable',
        description=(u'The path to the python executable. '
                     u'(i.e. /opt/python2.6/bin/python or just python)'),
        default='python')

zope.interface.directlyProvides(IPythonInterpreterFeature, IFeatureSchema)


class ITestingFeature(zope.interface.Interface):

    coverageDirectory = zope.schema.TextLine(
        title=u"Coverage Directory",
        description=u"Directory where test coverage data should be placed.",
        default=u"${buildout:directory}/coverage")

    coverageReportDirectory = zope.schema.TextLine(
        title=u'Coverage Report Directory',
        description=u'Directory where coverage reports should be generated',
        default=u'${buildout:directory}/coverage/report')

zope.interface.directlyProvides(ITestingFeature, IFeatureSchema)


class IScriptFeature(zope.interface.Interface):

    scriptName = zope.schema.TextLine(
        title=u'Script Name',
        description=(u'The name of the script that will '
                     u'be made available on the command line. '
                     u'Defaults to the name of the project.'),
        required=False)

    scriptFile = zope.schema.TextLine(
        title=u'Script File',
        description=u'The file where the script will be located',
        default=u"script.py")

    scriptFunction = zope.schema.TextLine(
        title=u'Script Function',
        description=u'The function in the script file that runs the script',
        default=u"main")

zope.interface.directlyProvides(IScriptFeature, IFeatureSchema)


class IDocumentationFeature(zope.interface.Interface):

    layoutTemplatePath = zope.schema.URI(
        title=u'Layout Template',
        description=u"URL for a layout template.  Leave blank for default",
        required=False)

    cssPath = zope.schema.URI(
        title=u'CSS url',
        description=(u'URL for a css file that should be used.  Leave blank '
                     u'for default.'),
        required=False)

    additionalEggs = zope.schema.List(
        title=u'Additional Packages',
        description=(u'Additional packages for which documentation should '
                     u'be built'),
        value_type=zope.schema.TextLine(),
        required=False)

zope.interface.directlyProvides(IDocumentationFeature, IFeatureSchema)
