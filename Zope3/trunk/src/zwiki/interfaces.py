##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""ZWiki Interface Declarations

This module defines the ZWiki relevant interfaces.

$Id$
"""
from zope.interface import Interface
from zope.schema import TextLine, List, SourceText, Choice

from zope.schema import Field
from zope.app.container.interfaces import IContained
from zope.app.container.interfaces import IContainer, IContentContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.event.interfaces import IObjectEvent

from zwiki import ZWikiMessageID as _ 

class IComment(Interface):
    """A simple Wiki Page comment.

    This interface specifies only the actual comment. Meta-data will be
    managed via annotations and the Dublin Core as usual.
    """

    title = TextLine(
        title=_(u"Title"),
        description=_(u"Comment Title"),
        default=u"",
        required=True)

    source = SourceText(
        title=_(u"Source Text"),
        description=_(u"Renderable source text of the comment."),
        default=u"",
        required=True)

    type = Choice(
        title=_(u"Source Type"),
        description=_(u"Type of the source text, e.g. structured text"),
        default=u"zope.source.rest",
        required = True,
        vocabulary = "SourceTypes")


class IWikiPage(IContainer, IContentContainer):
    """A single Wiki Page content object.

    The Wiki page is a simple content object that stores the content
    (source) and the source type of the wiki page.
    """

    def __setitem__(name, object):
        """Add a comment object."""

    __setitem__.precondition = ItemTypePrecondition(IComment)

    source = SourceText(
        title=_(u"Source Text"),
        description=_(u"Renderable source text of the Wiki Page."),
        default=u"",
        required=True)

    type = Choice(
        title=_(u"Source Type"),
        description=_(u"Type of the source text, e.g. structured text"),
        default=u"zope.source.rest",
        required = True,
        vocabulary = "SourceTypes")
        

class IWikiPageContained(IContained):
    """Objects that can be contained by Wiki Pages should implement this
    interface."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(IWikiPage))

    
class IWikiPageHierarchy(Interface):
    """This interface supports the virtual hierarchical structure of the Wiki
    Pages."""

    parents = List(
        title = _(u"Wiki Page Parents"),
        description = _(u"Parents of a Wiki"),
        value_type = TextLine(title=_(u"Parent Name"),
                              description=_(u"Name of the parent wiki page.")),
        required=False)

    def reparent(parents):
        """Reset the parents the Wiki page belongs to.

           The parents attribute is a list of unicode strings that contain the
           names of the parent wiki pages.
        """

    def path():
        """Return the object path of the virtual Wiki Hierarchy.

        The return value for this method should be a list of wiki objects
        describing the path.
        """

    def findChildren(recursive=True):
        """Returns a list of children for this wiki page.

        If the recursive is True, the method recurses into all children
        returning the entire sub-tree of this Wiki Page. Is the recursive
        argument set to False, only the first level of children will be
        returned.
        """
    
class IWiki(IContainer):
    """A simple container that manages Wikis inside itself."""

    def __setitem__(name, object):
        """Add a wiki page object."""

    __setitem__.precondition = ItemTypePrecondition(IWikiPage)


class IWikiContained(IContained):
    """Objects that contain Wikis should implement this interface."""
    __parent__ = Field(
        constraint = ContainerTypesConstraint(IWiki))


class IWikiPageEditEvent(IObjectEvent):
    """ an object event containing the old source in addition
    to the changed object
    """

    oldSource = SourceText(
        title=_(u"Previous Source Text"),
        description=_(u"Previous source text of the Wiki Page."),
        default=u"",
        required=True)

class IMailSubscriptions(Interface):
    """This interface allows you to retrieve a list of E-mails for
    mailings. In our context """

    def getSubscriptions():
        """Return a list of E-mails."""

    def addSubscriptions(emails):
        """Add a bunch of subscriptions, but one would be okay as well."""

    def removeSubscriptions(emails):
        """Remove a set of subscriptions."""
        

