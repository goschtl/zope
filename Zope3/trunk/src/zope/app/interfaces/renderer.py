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

$Id: renderer.py,v 1.2 2003/08/17 06:07:02 philikon Exp $
"""
from zope.interface import Interface

class ISourceTypeService(Interface):
    """The source type service keeps track of all interfaces that have been
    reported as a source type.

    Source Types are plain text input formats, such as ReST, STX or Plain
    Text. However, it could be also something like Python code.
    """

    def get(title, default=None):
        """Get the type interface by title. If the type was not found, return
        default."""

    def query(title):
        """Get the type interface by title. Throw an error, if not found."""

    def getAllTitles():
        """Return a list of all titles."""

    def createObject(title):
        """Creates an object that implements the interface (note these are
        just marker interfaces, so the object is minimal) that is registered
        with the title passed."""


class IGlobalSourceTypeService(ISourceTypeService):
    """Adds some write methods to the service, so that we can reguster new
    source types."""

    def provide(title, iface):
        """The title is the description of the source type and the interface
        is used to recognize the type."""


class ISource(Interface):
    """Simple base interface for all possible Wiki Page Source types."""

    def createComment(comment, number):
        """Create a comment from the comment content and the number of the
        comment.

        Various source types want to create comments in various different
        ways. This method allows us to specify a way to create comments for
        every different source type.
        """

class IPlainTextSource(ISource):
    """Marker interface for a plain text source. Note that an implementation
    of this interface should always derive from unicode or behave like a
    unicode class."""


class IStructuredTextSource(ISource):
    """Marker interface for a structured text source. Note that an
    implementation of this interface should always derive from unicode or
    behave like a unicode class."""


class IReStructuredTextSource(ISource):
    """Marker interface for a restructured text source. Note that an
    implementation of this interface should always derive from unicode or
    behave like a unicode class."""


class ISourceRenderer(Interface):
    """Objecrt implementing this interface are responsible for rendering an
    ISource objects to an output format. This is the base class for all
    possible output types."""

    def render(context):
        """Renders the source into another format.

        The context argument is passed, since some rendering might require
        some knowledge about the environment. If this turns out to be
        unnecessary, we can remove this attribute later."""
        

class IHTMLRenderer(ISourceRenderer):
    """Renders an ISource object to HTML."""
