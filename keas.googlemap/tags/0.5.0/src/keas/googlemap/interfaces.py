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
"""Keas Google Map Interfaces.

$Id$
"""
import zope.interface
import zope.schema
import zope.annotation.interfaces
import zope.interface.common.sequence


class IGoogleMapAPIKey(zope.interface.Interface):
    """A utility that provides a google map api key for a given domain."""

    key = zope.schema.ASCII(
        title=u"Google Maps API Key",
        description=u"The google maps API key for this domain name",
        required=True)


class IGeocodable(zope.interface.Interface):
    """Marker interface for objects that you can adapt to geocodes.

    i.e., IGeocode(object) could work for both IGeocode objects or
    IHaveGeocode objects.

    """


class IGeocode(IGeocodable):
    """A geocode representing a particular location on Earth."""

    latitude = zope.schema.Float(
        title=u"Latitude",
        description=u"The exact latitude of a place on Earth.",
        required=True)

    longitude = zope.schema.Float(
        title=u"Longitude",
        description=u"The exact longitude of a place on Earth.",
        required=True)

    def update(latitude, longitude):
        """Update the latitude and longitude with the given values."""


class IHaveGeocode(zope.annotation.interfaces.IAttributeAnnotatable,
                   IGeocodable):
    """A marker interface for object that have a geocode.

    The geocode is stored into the objects annotation and can be
    accessed by adapting the object to IGeocode."""


class ICenteredGeocodes(zope.interface.common.sequence.IReadSequence):
    """A sorted collection of Geocodes based around a center.

    Basically a list of (distance, geocode) pairs in ascending order by
    distance from the given center.
    """

    center = zope.schema.Object(
        title=u'Center',
        schema=IGeocodable,
        required=True)

    def add(codes):
        """Add geocodes to the collection"""


class IGeocodeQuery(zope.interface.Interface):
    """A query string that you could type into the google maps web
    interface.

    For example, a query string might be 1600 Pennsylvania Ave,
    Washington D.C."""

    query = zope.schema.TextLine(
        title=u"Geocode Query String",
        description=u"An address google maps can turn into a geocode.",
        required=True)
