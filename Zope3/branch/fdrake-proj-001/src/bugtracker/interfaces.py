##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bug Tracker Interfaces

Bag Tracker related interfaces.

$Id$
"""
from zope.interface import Interface, implements
from zope.schema import Text, TextLine, List, Dict, Choice, Field
from zope.schema.interfaces import IText
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized

from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.interfaces import IContentContainer
from zope.app.file.interfaces import IFile
from bugtracker import TrackerMessageID as _


class IBugTracker(IContainer, IContentContainer):
    """A Bug Tracker object represents a collection of bugs for a particular
    software or subject.

    Note that there is no specific interface for managing bugs, since the
    generic IContainer interface is sufficient.
    """

    title = TextLine(
        title = _(u"Title"),
        description = _(u"Title of the bug tracker."),
        required=True)


class IBugTrackerContained(IContained):
    """Objects that can be contained by bug trackers should implement this
    interface."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(IBugTracker))
    

class IBug(Interface):
    """A bug is the content object containing all necessary information that
    are relevant to a bug report.

    Note: I also included title in the interface, since I think it is part of
    the data and not the meta data of the bug content object.
    """

    title = TextLine(
        title = _(u"Title"),
        description = _(u"Title/Summary of the bug."),
        required=True)

    description = Text(
        title = _(u"Description"),
        description = _(u"Detailed Description of the bug."),
        required=True)

    submitter = TextLine(
        title = _(u"Submitter"),
        description = _(u"Name of the person that submitted the bug."),
        required=False)

    status = Choice(
        title = _(u"Status"),
        description = _(u"The current status of the bug."),
        default= 'new',
        required = True,
        vocabulary = "Stati")

    priority = Choice(
        title = _(u"Priority"),
        description = _(u"Specifies how urgent this bug is."),
        default= 'normal',
        required = True,
        vocabulary = "Priorities")

    type = Choice(
        title = _(u"Type"),
        description = _(u"Specifies of what nature the bug is."),
        default= 'bug',
        required = True,
        vocabulary = "BugTypes")

    release = Choice(
        title = _(u"Release"),
        description = _(u"Defines the release for which the bug is scheduled."),
        default = 'None',
        required = True,
        vocabulary = "Releases")

    owners = List(
        title = _(u"Owners"),
        description = _(u"List of people assigned as owners of the bug."),
        required=False,
        unique=True,
        value_type=Choice(vocabulary = "Users"))


class IBugContained(IContained):
    """Objects that can be contained by Bugs should implement this
    interface."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(IBug))


class IBugContainer(IContainer):
    """An object that contains bugs."""

    def __setitem__(name, object):
        """Add attachment."""

    __setitem__.precondition = ItemTypePrecondition(IBug)


class IBugDependencies(Interface):
    """This object handles the dependencies of a bug."""
    
    def addDependencies(self, dependencies):
        """Add the dependencies given to the existing list."""

    def deleteDependencies(self, dependencies):
        """Delete the dependencies given from the existing list."""

    dependencies = List(
        title = _(u"Dependencies"),
        description = _(u"Other bugs this bug depends on."),
        value_type = TextLine(title=_(u"Bug Id"),
                              description=_(u"Bug Id.")),
        required=False)

    def addDependents(self, dependents):
        """Add the dependents given to the existing list."""

    def deleteDependents(self, dependents):
        """Delete the dependents given from the existing list."""

    dependents = List(
        title = _(u"Dependents"),
        description = _(u"Other bugs that depend on this one"),
        value_type = TextLine(title=_(u"Bug Id"),
                              description=_(u"Bug Id.")),
        required=False)

    def findChildren(recursive=True):
        """Returns a list of children for this bug.

        If the recursive is True, the method recurses into all children
        returning the entire sub-graph of this Bug. Is the recursive
        argument set to False, only the first level of children will be
        returned.

        While circular references are okay (since dependencies are general
        graphs, not trees), this method must be aware of this fact and cannot
        just implement a plain old recursive algorithm. When a circle is
        detected, then simply cut off the search at this point.
        """


class IAttachment(Interface):
    """A marker interface for objects that can serve as Bug attachments."""


class IAttachmentContainer(IContainer, IContentContainer):
    """An object that contains attachments, i.e. comments and files."""

    def __setitem__(name, object):
        """Add attachment."""

    __setitem__.precondition = ItemTypePrecondition(IAttachment)


class IComment(IAttachment):
    """Simple comment for Bug.

    For now we assume the body to be structured text.
    """

    body = Text(
        title=_(u"Body"),
        description=_(u"Renderable body of the Comment."),
        default=u"",
        required=True)


class IManagableVocabulary(IVocabulary, IVocabularyTokenized):
    """Vocabulary that can be modified by adding and deleting terms.

    Note that this is a simple interface, where vocabularies are simple
    value-title mappings. The values should be preferibly in ASCII, so that
    there is no problem with encoding them in HTML.
    """

    def add(value, title):
        """Add a new vocabulary entry."""

    def delete(value):
        """Delete an entry from the vocabulary."""

    default = TextLine(
        title = _(u"Default"),
        description = _(u"Default value of the vocabulary."),
        required=True)

    
class IStatusVocabulary(IManagableVocabulary):
    """Manageable vocabulary that stores stati."""


class IReleaseVocabulary(IManagableVocabulary):
    """Manageable vocabulary that stores all releases."""


class IPriorityVocabulary(IManagableVocabulary):
    """Manageable vocabulary that stores all priority values."""


class IBugTypeVocabulary(IManagableVocabulary):
    """Manageable vocabulary that stores all type values."""


class IMailSubscriptions(Interface):
    """This interface allows you to retrieve a list of E-mails for
    mailings."""

    def getSubscriptions():
        """Return a list of E-mails."""

    def addSubscriptions(emails):
        """Add a bunch of subscriptions; one would be okay too."""

    def removeSubscriptions(emails):
        """Remove a set of subscriptions."""


# TODO: Remove once index is back
class ISearchableText(Interface):

    def getSearchableText():
        """Return searchable text."""
