"""Interfaces for zope.html.

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from i18n import _


class IEditableHtmlInformation(zope.interface.Interface):
    """Information about an HTML file or fragment."""

    isFragment = zope.schema.Bool(
        title=_("Is fragment?"),
        description=_("Set to true if the HTML should be handled as a"
                      " fragment to be composed to create a document."),
        required=True,
        readonly=False,
        )
