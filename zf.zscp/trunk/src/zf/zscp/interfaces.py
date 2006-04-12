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
"""ZSCP Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.interface.common.mapping
import zope.schema
import zope.schema.vocabulary
from zope.app.container.constraints import containers
from zope.app.container.constraints import contains

import zf.zscp.fields

CERTIFICATION_LEVELS = zope.schema.vocabulary.SimpleVocabulary([
    zope.schema.vocabulary.SimpleTerm(u'none', title=u'None'),
    zope.schema.vocabulary.SimpleTerm(u'listed', title=u'Listed'),
    zope.schema.vocabulary.SimpleTerm(u'level1', title=u'Level 1 Certified'),
    zope.schema.vocabulary.SimpleTerm(u'level2', title=u'Level 2 Certified'),
    zope.schema.vocabulary.SimpleTerm(u'level3', title=u'Level 3 Certified')
    ])

CERTIFICATION_ACTIONS = zope.schema.vocabulary.SimpleVocabulary([
    zope.schema.vocabulary.SimpleTerm(u'grant', title=u'Grant'),
    zope.schema.vocabulary.SimpleTerm(u'revoke', title=u'Revoke'),
    zope.schema.vocabulary.SimpleTerm(u'warn', title=u'Warn'),
    ])

class IRepositoryInitializedEvent(zope.interface.Interface):
    """Event fired after a repository was initialized."""
    repository = zope.interface.Attribute('The initialized repository')

class RepositoryInitializedEvent(object):
    zope.interface.implements(IRepositoryInitializedEvent)

    def __init__(self, repository):
        self.repository = repository


class IPackageEvent(zope.interface.Interface):
    """An event that involves a package."""
    package = zope.interface.Attribute('The package that was acted upon')

class PackageEvent(object):
    zope.interface.implements(IPackageEvent)
    def __init__(self, pkg):
        self.package = pkg


class IPackageRegisteredEvent(IPackageEvent):
    """An event fired after the package has been registered with the ZSCP."""

class PackageRegisteredEvent(PackageEvent):
    pass


class IPackageUnregisteredEvent(IPackageEvent):
    """An event fired after the package has been unregistered with the ZSCP."""

class PackageUnregisteredEvent(PackageEvent):
    pass


class IPackageUpdateddEvent(IPackageEvent):
    """An event fired after the package has been updated."""

class PackageUpdatedEvent(PackageEvent):
    pass


class IContact(zope.interface.Interface):
    """A contact"""

    name = zope.schema.TextLine(
        title=u"Contact Name",
        description=u"The full name of the contact person.",
        required=True)

    email = zope.schema.TextLine(
        title=u"Contact E-mail",
        description=u"The E-mail address of the contact person.",
        required=False)


class IRelease(zope.interface.Interface):
    """A release of a package."""

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"The name under which the package will be known for this "
                    u"release.",
        required=True)

    version = zope.schema.TextLine(
        title=u"Version",
        description=u"This field describes the version number of the release.",
        required=True)

    codename = zope.schema.TextLine(
        title=u"Codename",
        description=u"The code name of the release.",
        required=False)

    date = zf.zscp.fields.Date(
        title=u"Date",
        description=u"The date on which the release was made.",
        required=True)

    certification = zope.schema.Choice(
        title=u"Certification",
        description=u"The certification level of the package at the date "
                    u"of the release.",
        vocabulary=CERTIFICATION_LEVELS,
        required=True,
        default=u'none')

    package = zope.schema.URI(
        title=u"Package",
        description=u"The URL to the installation package file.",
        required=True)

    source = zope.schema.URI(
        title=u"Source",
        description=u"The URL to the repository location. It should be "
                    u"possible to use this URL to make a checkout.",
        required=False)

    dependencies = zope.schema.List(
        title=u"Dependencies",
        description=u"A set of dependencies to other packages. Each "
                    u"dependency must contain the full name of the package "
                    u"and the version number.",
        value_type=zope.schema.TextLine(title=u'Dependency'),
        required=False)

    announcement = zope.schema.URI(
        title=u"Announcement",
        description=u"A link to the announcement of the release.",
        required=False)

    releaseManager = zope.schema.Object(
        title=u"Release Manager",
        description=u"The release manager of the release.",
        schema=IContact,
        required=False)

    pressContact = zope.schema.Object(
        title=u"Press Contact",
        description=u"The press contact of the release.",
        schema=IContact,
        required=False)


class ICertification(zope.interface.Interface):
    """A certification."""

    action = zope.schema.Choice(
        title=u"Action",
        description=u"The action describes whether a certification was "
                    u"granted or revoked. Upon violations (as defined "
                    u"in section 2.8 of the ZSCP proposal), a certification "
                    u"manager can also issue a warning.",
        vocabulary=CERTIFICATION_ACTIONS,
        required=True)

    sourceLevel = zope.schema.Choice(
        title=u"Source Level",
        description=u"The original certification level before this "
                    u"certification action was executed.",
        vocabulary=CERTIFICATION_LEVELS,
        required=True)

    targetLevel = zope.schema.Choice(
        title=u"Target Level",
        description=u"The final certification level after this "
                    u"certification action was executed.",
        vocabulary=CERTIFICATION_LEVELS,
        required=True)

    date = zf.zscp.fields.Date(
        title=u"Date",
        description=u"The date on which the certification action was executed.",
        required=True)

    certificationManager = zope.schema.Object(
        title=u"Certification Manager",
        description=u"The certification manager that executed the "
                    u"certification action.",
        schema=IContact,
        required=True)

    comments = zope.schema.Text(
        title=u"Codename",
        description=u"This field can contain arbitrary comments about the "
                    u"certification action.",
        required=False)


class IPublication(zope.interface.Interface):
    """Publication data."""

    packageName = zope.schema.Id(
        title=u"Package Name",
        description=u"The dotted Python path of the package.",
        required=True)

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"The commonly used name of the package.",
        required=True)

    summary = zope.schema.TextLine(
        title=u"Summary",
        description=u"A short description or summary of the package. It is "
                    u"also often interpreted as the title.",
        required=True)

    description = zope.schema.Text(
        title=u"Description",
        description=u"A detailed description of the package's functionality. "
                    u"While it should contain some detail, it should not "
                    u"duplicate the documentation of the README.txt file.",
        required=False)

    homePage = zope.schema.URI(
        title=u"Homepage",
        description=u"A URL to the homepage of the package.",
        required=False)

    author = zope.schema.List(
        title=u"Author Names",
        description=u"The names of the authors of the package.",
        value_type=zope.schema.TextLine(title=u'Name'),
        required=False)

    authorEmail = zope.schema.List(
        title=u"Author Emails",
        description=u"The E-mails of the authors of the package.",
        value_type=zope.schema.TextLine(title=u'E-mail'),
        required=False)

    license = zope.schema.List(
        title=u"Licenses",
        description=u"The software license(s) of the package.",
        value_type=zope.schema.TextLine(title=u'License'),
        required=False)

    platform = zope.schema.List(
        title=u"Supported Platforms",
        description=u"The operating system/platform the package is known to "
                    u"run on. This field can be specified multiple times. "
                    u"``All`` may be used, if the package is available "
                    u"on all platforms Python is running on, i.e. the "
                    u"package is pure Python code.",
        value_type=zope.schema.TextLine(title=u'Platform'),
        required=False,
        default=[u'All'])

    classifier = zope.schema.List(
        title=u"Classifiers",
        description=u"A classification entry identifying the package.",
        value_type=zope.schema.TextLine(title=u'Classifier'),
        required=False)

    developersMailinglist = zope.schema.TextLine(
        title=u"Developers Mailinglist",
        description=u"The E-mail address of the developers mailing list.",
        required=False)

    usersMailinglist = zope.schema.TextLine(
        title=u"Users Mailinglist",
        description=u"The E-mail address of the users mailing list.",
        required=False)

    issueTracker = zope.schema.URI(
        title=u"Issue Tracker",
        description=u"A URL to the issue tracker of the package, where new "
                    u"issues/bugs/requests can be reported.",
        required=False)

    repositoryLocation = zope.schema.URI(
        title=u"Source Repository",
        description=u"The URL to the repository. The URL should be usable "
                    u"to actually check out the package.",
        required=False)

    repositoryWebLocation = zope.schema.URI(
        title=u"Browsable Repository",
        description=u"The URL to the repository's browsable HTML UI.",
        required=False)

    certificationLevel = zope.schema.Choice(
        title=u"Certification Level",
        description=u"Describes the certification level of the package.",
        vocabulary=CERTIFICATION_LEVELS,
        required=False)

    certificationDate = zf.zscp.fields.Date(
        title=u"Certification Date",
        description=u"The date at which the certification was received.",
        required=False)

    metadataVersion = zope.schema.TextLine(
        title=u"Metadata Version",
        description=u"This is the version number of this package meta-data.",
        required=True)


class IPackage(zope.interface.Interface):
    """Package"""

    containers('zf.zscp.interfaces.IZSCPRepository')

    name = zope.schema.Id(
        title=u"Package Name",
        description=u"The dotted Python path of the package.",
        required=True)

    publication = zope.schema.Object(
        title=u"Publication Information",
        schema=IPublication,
        required=True)

    releases = zope.schema.List(
        title=u"Releases",
        value_type=zope.schema.Object(schema=IRelease),
        required=True)

    certifications = zope.schema.List(
        title=u"Certifications",
        value_type=zope.schema.Object(schema=ICertification),
        required=True)


class IZSCPRepository(zope.interface.common.mapping.IEnumerableMapping):
    """ZSCP Repository."""

    containers('zf.zscp.website.interfaces.IZSCPSite')

    contains(IPackage)    

    svnRoot = zope.schema.URI(
        title=u"SVN Repository Root",
        description=u"A SVN URI that can be used to checkout the package data.",
        required=True)

    localRoot = zope.schema.BytesLine(
        title=u"Local Repository Root",
        description=u"The directory on the server in to which the packages "
                    u"are checked out.",
        required=True)

    username = zope.schema.TextLine(
        title=u"User name",
        description=u"The username used without SSH keys.",
        required=False)

    password = zope.schema.Password(
        title=u"SSH Password",
        description=u"The password used for the user or for a shh key.",
        required=False)

    def initialize():
        """Initialize the ZSCP repository."""

    def register(pkg):
        """Register a package with ZSCP."""

    def unregister(pkg):
        """Unregister a package from ZSCP"""

    def update(pkg):
        """Update the local copy of the ZSCP data."""

    def fetch(all=False):
        """Fetch all package names from the SVN repository.

        If ``all`` is true, then return all packages of the repository,
        regardless of their ZSCP status.
        """
