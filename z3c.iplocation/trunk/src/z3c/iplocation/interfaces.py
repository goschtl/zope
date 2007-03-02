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
"""IP Locator Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
from z3c.schema import ip

class ILocation(zope.interface.Interface):
    """A location for a given IP range."""

    ipFrom = ip.IPAddress(
        title=u'IP From',
        description=u'First IP address in Netblock.',
        required=True)

    ipTo = ip.IPAddress(
        title=u'IP To',
        description=u'Last IP address in Netblock.',
        required=True)

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'The name of the location of the IP range.',
        required=True)


class IIPligenceLiteLocation(ILocation):
    """An IPligence compatible location for the lite version of the data."""

    decimalFrom = zope.schema.Int(
        title=u'Decimal IP From',
        description=u'First IP address in Netblock as a decimal.',
        required=True)

    decimalTo = zope.schema.Int(
        title=u'Decimal IP To',
        description=u'Last IP address in Netblock as a decimal.',
        required=True)

    countryCode = zope.schema.ASCIILine(
        title=u'Country Code',
        description=u'Two characters country code based on ISO 3166.',
        min_length=2,
        max_length=2,
        required=True)

    countryName = zope.schema.ASCIILine(
        title=u'Country Name',
        description=u'Country name based on ISO 3166.',
        required=True)

    continentCode = zope.schema.ASCIILine(
        title=u'Continent Code',
        description=u'Two characters continent code based on ISO 3166.',
        min_length=2,
        max_length=2,
        required=True)

    continentName = zope.schema.ASCIILine(
        title=u'Continent Name',
        description=u'Continent name based on ISO 3166.',
        required=True)


class IIPligenceBasicLocation(IIPligenceLiteLocation):
    """An IPligence compatible location for the basic version of the data."""

    owner = zope.schema.ASCIILine(
        title=u'Owner',
        description=u'Company owner or Internet Service Provider.',
        required=True)

    timeZone = zope.schema.ASCIILine(
        title=u'Time Zone',
        description=u'Time Zone',
        required=True)

    regionCode = zope.schema.ASCIILine(
                    title=u'Region Code',
        description=u'Two characters region or state code.',
        min_length=2,
        max_length=2,
        required=False)

    regionName = zope.schema.ASCIILine(
        title=u'Region Name',
        description=u'Region or State name.',
        required=False)


class IIPligenceMaxLocation(IIPligenceBasicLocation):
    """An IPligence compatible location for the max version of the data."""

    cityName = zope.schema.ASCIILine(
        title=u'City Name',
        description=u'City name.',
        required=True)

    countyName = zope.schema.ASCIILine(
        title=u'County Name',
        description=u'County name.',
        required=False)

    latitude = zope.schema.Float(
        title=u'Latitude',
        description=u'Latitude.',
        required=True)

    longitude = zope.schema.Float(
        title=u'Longitude',
        description=u'Longitude.',
        required=True)


class IIPLocator(zope.interface.Interface):
    """Component to retrieve the location of an IP address."""

    def get(ip, default=None):
        """Return a location for the given IP.

        The location must at least implement ``ILocation``, but might also
        implement any of the extended location interfaces.

        If no location was found, return the default value.
        """

class IIPLocatorManagement(zope.interface.Interface):
    """Manage IP Locator data."""

    def add(location):
        """Add an IP location.

        If the location is already in the locator, ignore the request.
        """

    def remove(location):
        """Remove an IP location.

        If the location is not in the locator, ignore the request.
        """
