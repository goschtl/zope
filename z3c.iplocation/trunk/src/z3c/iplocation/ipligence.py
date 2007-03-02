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
"""IP Locator for IPligence Data

$Id$
"""
__docformat__ = "reStructuredText"
import csv
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.iplocation import interfaces, locator

class LiteLocation(locator.Location):
    zope.interface.implements(interfaces.IIPligenceLiteLocation)

    decimalFrom = FieldProperty(
        interfaces.IIPligenceLiteLocation['decimalFrom'])
    decimalTo = FieldProperty(
        interfaces.IIPligenceLiteLocation['decimalTo'])
    countryCode = FieldProperty(
        interfaces.IIPligenceLiteLocation['countryCode'])
    countryName = FieldProperty(
        interfaces.IIPligenceLiteLocation['countryName'])
    continentCode = FieldProperty(
        interfaces.IIPligenceLiteLocation['continentCode'])
    continentName = FieldProperty(
        interfaces.IIPligenceLiteLocation['continentName'])

    def __init__(self, decimalFrom, decimalTo, countryCode, countryName,
                 continentCode, continentName):
        self.decimalFrom = int(decimalFrom)
        self.decimalTo = int(decimalTo)
        self.countryCode = countryCode
        self.countryName = countryName
        self.continentCode = continentCode
        self.continentName = continentName

    @property
    def ipFrom(self):
        return locator.getIP(self.decimalFrom)

    @property
    def ipTo(self):
        return locator.getIP(self.decimalTo)

    @property
    def name(self):
        return unicode(self.countryName)


class BasicLocation(LiteLocation):
    zope.interface.implements(interfaces.IIPligenceBasicLocation)

    owner = FieldProperty(
        interfaces.IIPligenceBasicLocation['owner'])
    timeZone = FieldProperty(
        interfaces.IIPligenceBasicLocation['timeZone'])
    regionCode = FieldProperty(
        interfaces.IIPligenceBasicLocation['regionCode'])
    regionName = FieldProperty(
        interfaces.IIPligenceBasicLocation['regionName'])

    def __init__(self, decimalFrom, decimalTo, countryCode, countryName,
                 continentCode, continentName, owner, timeZone,
                 regionCode, regionName):
        super(BasicLocation, self).__init__(
            decimalFrom, decimalTo, countryCode, countryName,
            continentCode, continentName)
        self.owner = owner
        self.timeZone = timeZone
        self.regionCode = regionCode or None
        self.regionName = regionName or None


class MaxLocation(BasicLocation):
    zope.interface.implements(interfaces.IIPligenceMaxLocation)

    cityName = FieldProperty(
        interfaces.IIPligenceMaxLocation['cityName'])
    countryName = FieldProperty(
        interfaces.IIPligenceMaxLocation['countryName'])
    latitude = FieldProperty(
        interfaces.IIPligenceMaxLocation['latitude'])
    longitude = FieldProperty(
        interfaces.IIPligenceMaxLocation['longitude'])

    def __init__(self, decimalFrom, decimalTo, countryCode, countryName,
                 continentCode, continentName, owner, timeZone,
                 regionCode, regionName, cityName, countyName,
                 latitude, longitude):
        super(MaxLocation, self).__init__(
            decimalFrom, decimalTo, countryCode, countryName, continentCode,
            continentName, owner, timeZone, regionCode, regionName)
        self.cityName = cityName
        self.countyName = countyName or None
        self.latitude = float(latitude)
        self.longitude = float(longitude)


def createLocator(file, klass=LiteLocation):
    liteLocator = locator.IPLocator()
    for row in csv.reader(file):
        loc = klass(*row)
        liteLocator.add(loc, loc.decimalFrom, loc.decimalTo)
    return liteLocator
