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
"""ZWiki Interface Declarations

This module defines the ZWiki relevant interfaces.

$Id: interfaces.py,v 1.1 2004/02/27 11:06:58 philikon Exp $
"""
from zope.interface import Interface
from zope.schema import TextLine, List, SourceText
from zope.schema.vocabulary import VocabularyField

#from zope.app.interfaces.container import IContentContainer
from zope.schema import Field
from zope.app.interfaces.container import IContained
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.interfaces.container import IContainer
from zope.app.i18n import ZopeMessageIDFactory as _ 

class IWikiPage(Interface):
    """A single Wiki Page content object.

    The Wiki page is a simple content object that stores the content
    (source) and the source type of the wiki page."""

    source = SourceText(
        title=_(u"Source Text"),
        description=_(u"Renderable source text of the Wiki Page."),
        default=u"",
        required=True)

    type = VocabularyField(
        title=_(u"Source Type"),
        description=_(u"Type of the source text, e.g. structured text"),
        default=u"reStructured Text (reST)",
        required = True,
        vocabulary = "SourceTypes")

    def append(source):
        """Append some text to the existing source text."""

    def comment(source, user):
        """Comment on the current Wiki; add comment to source."""

    def getCommentCounter():
        """Returns the amount of written comments for this wiki page."""
        

class IWikiPageHierarchy(Interface):
    """This interface supports the virtual hierarchical structure of the Wiki
    Pages."""

    parents = List(
        title = _(u"Wiki Page Parents"),
        description = _(u"Parents of a a Wiki"),
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

        XXX: Wiki Pages can have several parents, so that we should be able to
        have multiple paths; but let's not worry about that right now. At some
        point this needs to be done though.
        """

    def findChildren(recursive=True):
        """Returns a list of children for this wiki page.

        If the recursive is True, the method recurses into all children
        returning the entire sub-tree of this Wiki Page. Is the recursive
        argument set to False, only the first level of children will be
        returned.
        """
    
class IWiki(IContainer):
    def __setitem__(name, object):
        """Add a poll"""
    __setitem__.precondition = ItemTypePrecondition(IWikiPage)


class IWikiContained(IContained):
    __parent__ = Field(
        constraint = ContainerTypesConstraint(IWiki))



class IMailSubscriptions(Interface):
    """This interface allows you to retrieve a list of E-mails for
    mailings. In our context """

    def getSubscriptions():
        """Return a list of E-mails."""

    def addSubscriptions(emails):
        """Add a bunch of subscriptions, but one would be okay as well."""

    def removeSubscriptions(emails):
        """Remove a set of subscriptions."""
        

