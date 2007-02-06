##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Quick Entry Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface

class IProcessor(zope.interface.Interface):
    """A processor for a quick entry text."""

    separationCharacter = zope.interface.Attribute(
        'Each value is separated by this character.')

    plugins = zope.interface.Attribute(
        'A sequence of plugin classes that are used to parse the text.')

    def parse(text):
        """Parse the text into a tuple of plugin instances."""

    def process(text, context=None):
        """Process a quick entry text.

        The context can be used by plugins to look up values.

        The returned value should be a dictionary of extracted variables.
        """

class IExecutingProcessor(IProcessor):
    """A processor that can apply the parsed data to a context."""

    def apply(text, context):
        """Apply data once it is parsed.

        The data is applied on the context.
        """


class IPlugin(zope.interface.Interface):
    """A plugin for a particular piece of the quick entry text."""

    text = zope.interface.Attribute(
        'The text that is going to be converted into values. '
        'The processor will fill this attribute after the initial text is set.')

    def canProcess():
        """Determine whether the plugin can handle the text.

        Returns a boolean stating the result.
        """

    def process(context):
        """Process the text to create the varaiable names.

        The result will be a dictionary from variable name to value. While
        plugins often will only produce one variable, they can produce several.

        If processing fails for some reason, a ``ValueError`` with a detailed
        explanation must be raised.
        """

class IExecutingPlugin(IPlugin):
    """A plugin that can apply the parsed data to a context."""

    def apply(text, context=None):
        """Apply data once it is parsed.

        The data is applied on the context.
        """
