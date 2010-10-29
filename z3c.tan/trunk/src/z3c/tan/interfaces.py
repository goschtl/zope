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
"""TAN Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import string
import zope.interface
import zope.schema
import zope.app.security.vocabulary
import zope.app.container.interfaces
from zope.app.container import constraints

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('z3c.tan')


class ITANInformation(zope.interface.Interface):
    """Component providing all information about a TAN."""
    constraints.containers('.ITANManager')

    tan = zope.schema.TextLine(
        title=_("TAN"),
        description=_("The TAN number/code itself."),
        required=True)

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Title as which the TAN is known."),
        required=False)

    description = zope.schema.Text(
        title=_("Description"),
        description=_("A short description describing the TAN's purpose."),
        required=False)

    allowedPrincipals = zope.schema.Tuple(
        title=_("Allowed Principals"),
        value_type=zope.schema.Choice(
            source=zope.app.security.vocabulary.PrincipalSource()),
        description=_(
            "List of principals (ids) that are allowed to use the TAN"),
        missing_value=None,
        default=None,
        required=False)


class ITANAlreadyUsed(zope.interface.Interface):
    """Exception expressing that a TAN had been used already."""

class TANAlreadyUsed(ValueError):
    zope.interface.implements(ITANAlreadyUsed)


class ITANManager(zope.app.container.interfaces.IContainer):
    """A TAN Manager.

    The TAN manager is responsible for not allowing to repeat TANs.
    """
    constraints.contains(ITANInformation)

    def add(tan):
        """Add a tan to the manager."""


class ITANGenerator(zope.interface.Interface):
    """Generates TANs for consumption."""

    def generate(manager, amount=1, title=None, description=None,
                 allowedPrincipals=None):
        """Generate *valid* TANs and add them to the manager.

        Return a list of new TAN ids.

        ``manager``
            The TAN manager to which the TANs will be added.

        ``amount``
            Specifies how many TANs should be generated.

        ``title``
            The title for the TAN information object that will be added to
            every generated TAN.

        ``description``
            The description for the TAN information object that will be added
            to every generated TAN.

        ``allowedPrincipals``
            The description for the TAN information object that will be added
            to every generated TAN.
        """

class ICommonTANGenerator(ITANGenerator):
    """Allows to specify some common sense options."""

    length = zope.schema.Int(
        title=_("Length"),
        description=_("The total length in characters of the TAN."),
        default=8,
        required=True)

    characters = zope.schema.BytesLine(
        title=_("Characters"),
        description=_("A list of allowed characters."),
        default=string.letters[26:]+string.digits,
        required=True)
