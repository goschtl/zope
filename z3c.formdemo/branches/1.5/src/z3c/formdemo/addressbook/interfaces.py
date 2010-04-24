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
"""Address Book Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
from zope.schema import vocabulary

AddressNamesVocabulary = vocabulary.SimpleVocabulary((
    vocabulary.SimpleTerm('home', title=u'Home'),
    vocabulary.SimpleTerm('work', title=u'Work'),
    vocabulary.SimpleTerm('other', title=u'Other')
    ))

class IAddress(zope.interface.Interface):
    """An address."""

    street = zope.schema.TextLine(
        title=u'Street',
        description=u'Street name and number.')

    city = zope.schema.TextLine(
        title=u'City',
        description=u'City.')

    state = zope.schema.TextLine(
        title=u'State',
        description=u'State or Province.')

    zip = zope.schema.TextLine(
        title=u'ZIP',
        description=u'ZIP Code.')


class IEMail(zope.interface.Interface):
    """An E-mail address."""

    user = zope.schema.TextLine(
        title=u'User')

    host = zope.schema.TextLine(
        title=u'Host')

    fullAddress = zope.schema.TextLine(
        title=u'E-mail Address',
        description=u'The full E-mail address.')


class IPhone(zope.interface.Interface):
    """A phone number."""

    countryCode = zope.schema.TextLine(
        title=u'Country Code',
        default=u'1')

    areaCode = zope.schema.TextLine(
        title=u'Area Code')

    number = zope.schema.TextLine(
        title=u'Number')

    extension = zope.schema.TextLine(
        title=u'Extension',
        required=False)


class IContact(zope.interface.Interface):
    """A contact in the address book."""

    firstName = zope.schema.TextLine(
        title=u'First Name',
        description=u'First name of the person.')

    lastName = zope.schema.TextLine(
        title=u'Last Name',
        description=u'Last name of the person.')

    birthday = zope.schema.Date(
        title=u'Birthday',
        description=u'Birthday of the person.',
        required=False)

    addresses = zope.schema.Dict(
        title=u'Addresses',
        description=u'A mapping of addresses',
        key_type=zope.schema.Choice(
            __name__='addressName',
            vocabulary=AddressNamesVocabulary),
        value_type=zope.schema.Object(schema=IAddress))

    emails = zope.schema.List(
        title=u'E-mails',
        description=u'E-mails of the person.',
        value_type=zope.schema.Object(schema=IEMail))

    homePhone = zope.schema.Object(
        title=u'Home Phone',
        description=u'Home Phone Number.',
        schema=IPhone)

    cellPhone = zope.schema.Object(
        title=u'Cell Phone',
        description=u'Cell Phone Number.',
        schema=IPhone,
        required=False)

    workPhone = zope.schema.Object(
        title=u'Work Phone',
        description=u'Work Phone Number.',
        schema=IPhone,
        required=False)
