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
from zope.app.container.interfaces import IContainer


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

    def setTitle(title):
        """Set the title of the Topic."""
        
    def getTitle():
        """Get the title of the Topic."""

    def setContentPath(filename, doc_type="stx"):
        """Tell the Topic where it can find"""

    def getContent():
        """Get the content of the Topic's file and return it. If the contents
        is STX or Plain Text, the content is processed to HTML at this
        point."""

        
class IOnlineHelp(IOnlineHelpTopic):
    """This service manages all the HelpTopics."""

    def getTopicsForInterfaceAndView(interface=None, view=None):
        """Returns a list of Topics that were registered to be
        applicable to a particular view of an interface."""

    def registerHelpTopic(parent_path, title, doc_path, doc_type, 
                          interface=None, view=None):
        """This method registers a topic at the correct place.

           parent_path -- Location of this topic's parent in the OnlineHelp
           tree.

           title -- Specifies title of the topic. This title will be used in
           the tree as Identification.

           doc_path -- Specifies where the file that contains the topic
           content is located.

           doc_type -- Defines the type of document this topic will
           be. Examples (not necessarily available) are: TXT, reST, HTML

           interface -- Name of the interface for which the help topic is
           being registered. This can be optional, since not all topics must
           be bound to a particular interface.

           view -- This attribute specifies the name of the view for which
           this topic is registered. Note that this attribute is also
           optional.
        """
