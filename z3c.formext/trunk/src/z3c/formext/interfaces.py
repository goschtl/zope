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
"""ExtJS integration.

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from z3c.form.interfaces import ITextWidget
from z3c.form.interfaces import ISingleCheckBoxWidget
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IButton
from z3c.form.interfaces import IButtonAction
from z3c.form.interfaces import ISelectionManager
from z3c.formjs.interfaces import IAJAXRequestHandler
from z3c.versionedresource.interfaces import IVersionedResource


class IClientButton(IButton):
    success = zope.schema.ASCIILine(
        title=u'Success function',
        required=False)

    failure = zope.schema.ASCIILine(
        title=u'Failure function',
        required=False)

class IClientButtonAction(IButtonAction):
    success = zope.schema.ASCIILine(
        title=u'Success function',
        required=False)

    failure = zope.schema.ASCIILine(
        title=u'Failure function',
        required=False)


class IJSModule(IVersionedResource):
    """A javascript module."""


class IExtJSDateWidget(ITextWidget):
    """Marker interface for an ExtJSDate widget.

    When ExtJS sends back data for a date, it does not fit the
    standard l10n locale specific date format.  This Widget thus has a
    special data converter associated with it that handles the format
    given by ExtJS.
    """


class IExtJSSingleCheckBoxWidget(ISingleCheckBoxWidget):
    """Marker interface for an ExtJSSingleChexkBox widget.

    When ExtJS sends back data for a checkbox, it does not fit the
    standard checkbox format.  This Widget thus has a special data
    converter associated with it that handles the format given by
    ExtJS.
    """


class IExtJSComponent(zope.interface.Interface):
    """An object that represents and ExtJS component.

    This object provides a serialized representation of itself that
    can be used as the config object for an extjs component.
    """

    def getConfig(json=False):
        """Return the configuration object of this component.

        If the json flag is passed, the result is returned in json
        serialization form.
        """

class IJSProperties(ISelectionManager):
    """A Selection Manager for JavaScript Properties"""


class IExtJSForm(IAJAXRequestHandler, IForm):

    jsonResponse = zope.schema.Field(
        title=u'JSON Response',
        description=u'The response data structure')

    response = zope.schema.Text(
        title=u'Response',
        description=u'A json encoded response')
