##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""OnlineHelp Interfaces

These are the interfaces designed for the OnlineHelp system.

$Id$
"""
from zope.schema import TextLine, SourceText, Choice
from zope.app.container.interfaces import IContainer
from zope.i18n import MessageIDFactory
from zope.app.file.interfaces import IFile, IFileContent

_ = MessageIDFactory('messageboard')

class IOnlineHelpTopic(IContainer):
    """A Topic is one help page that you could view. Topics will be able to
    contain other Topics and so on.

    You can also associate a Topic with a particular view.
    
    The Topic's content can be in the following three forms:
    Plain Text, HTML and Structured Text (STX). The Content is usually
    stored in a file and not the Topic itself. The file is only read
    when required.
    
    Note that all the Sub-Topic management is done by the IContainer
    interface. 
    """

    title = TextLine(
        title = _(u"Help Topic Title"),
        description = _(u"The Title of a Help Topic"),
        default = _(u"Help Topic"),
        required = True)

    source = SourceText(
        title=_(u"Source Text"),
        description=_(u"Renderable source text of the topic."),
        default=u"",
        required=True,
        readonly=True)

    path = TextLine(
        title = _(u"Path to the Topic"),
        description = _(u"The Path to the Definition of a Help Topic"),
        default = u"./README.TXT",
        required = True)

    type = Choice(
        title=_(u"Source Type"),
        description=_(u"Type of the source text, e.g. structured text"),
        default=u"zope.source.rest",
        required = True,
        vocabulary = "SourceTypes")

    def addResources(resources):
        """ Add resources to this Help Topic.
        The resources must be located in the same directory
        as the Help Topic itself."""

class IOnlineHelp(IOnlineHelpTopic):
    """This service manages all the HelpTopics."""

    def getTopicsForInterfaceAndView(interface, view=None):
        """Returns a list of Topics that were registered to be
        applicable to a particular view of an interface."""

    def getTopicForObjectAndView(obj, view=None):
        """Returns the first matching help topic for
        the interfaces provided by obj."""

    def registerHelpTopic(parent_path, id, title, doc_path,  
                          interface=None, view=None):
        """This method registers a topic at the correct place.

           parent_path -- Location of this topic's parent in the OnlineHelp
           tree.

           id -- Specifies the id of the topic 

           title -- Specifies title of the topic. This title will be used in
           the tree as Identification.

           doc_path -- Specifies where the file that contains the topic
           content is located.

           interface -- Name of the interface for which the help topic is
           being registered. This can be optional, since not all topics must
           be bound to a particular interface.

           view -- This attribute specifies the name of the view for which
           this topic is registered. Note that this attribute is also
           optional.
        """

class IOnlineHelpResource(IFile, IFileContent):
    """A resource, which can be used in a help topic """

    path = TextLine(
        title = _(u"Path to the Resource"),
        description = _(u"The Path to the Resource, assumed to be "
                        "in the same directory as the Help Topic"),
        default = u"",
        required = True)
