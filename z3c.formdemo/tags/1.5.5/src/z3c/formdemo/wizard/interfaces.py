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
"""Person Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
from z3c.form import interfaces


# ----[ Wizard Interfaces ]---------------------------------------------------

class ISaveButton(interfaces.IButton):
    """A button that causes the step data to be saved."""

class IBackButton(interfaces.IButton):
    """A button that returns to some previous state or screen."""

class IForwardButton(interfaces.IButton):
    """A button that returns to some next state or screen."""

class IStep(zope.interface.Interface):
    """An interface marking a step sub-form."""

    def isComplete():
        """Determines whether a step is complete."""

class IWizard(zope.interface.Interface):
    """An interface marking the controlling wizard form."""

    def isComplete():
        """Determines whether the wizard is complete."""

    def getCurrentStep():
        """Return the current step as an instance."""

    def isFirstStep():
        """Determine whether the current step is the first one."""

    def isLastStep():
        """Determine whether the current step is the last one."""


# ----[ Content Interfaces ]--------------------------------------------------

class IAddress(zope.interface.Interface):

    street = zope.schema.TextLine(
        title=u'Street',
        description=u'The street address.',
        default=u'',
        missing_value=u'',
        required=True)

    zip = zope.schema.TextLine(
        title=u'Zip',
        description=u'The zip code of the location.',
        default=u'',
        missing_value=u'',
        required=True)

    city = zope.schema.TextLine(
        title=u'City',
        description=u'The city.',
        default=u'',
        missing_value=u'',
        required=True)


class IPersonalInfo(IAddress):

    lastName = zope.schema.TextLine(
        title=u'Last Name',
        description=u'The last name of the person.',
        default=u'',
        missing_value=u'',
        required=True)

    firstName = zope.schema.TextLine(
        title=u'First Name',
        description=u'The first name of the person.',
        default=u'',
        missing_value=u'',
        required=True)

    phone = zope.schema.TextLine(
        title=u'Phone',
        description=u'The phone number.',
        default=u'',
        missing_value=u'',
        required=False)

    email = zope.schema.TextLine(
        title=u'Email',
        description=u'The email address.',
        required=False)


class IEmployerInfo(IAddress):

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'The name of the employer.',
        default=u'',
        missing_value=u'',
        required=True)


class IPerson(IPersonalInfo):

    father = zope.schema.Object(
        title=u'Father',
        description=u"Father's personal info.",
        schema=IPersonalInfo,
        required=True)

    mother = zope.schema.Object(
        title=u'Mother',
        description=u"Mother's personal info.",
        schema=IPersonalInfo,
        required=True)

    employer = zope.schema.Object(
        title=u'Employer',
        description=u"Employer's info.",
        schema=IEmployerInfo,
        required=True)
