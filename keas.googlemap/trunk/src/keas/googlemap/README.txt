Google Maps API (keas.googlemaps)
=================================

The ``keas.googlemap`` package provides utilities for working with google
maps in Zope 3.

  >>> from keas.googlemap import interfaces

Basic Geocodes
--------------

We have a very basic geocode implementation.

  >>> from keas.googlemap import geocode
  >>> geo = geocode.Geocode()
  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(interfaces.IGeocode, geo)
  True
  >>> print geo
  Geocode(0.0, 0.0)

By default, we have a latitude and longitude of 0.0:

  >>> geo.latitude
  0.0
  >>> geo.longitude
  0.0

We can update both values using the ``update`` method:

  >>> geo.update(5.4, 4.3)
  >>> print geo
  Geocode(5.4, 4.3)


Querying for Geocodes
---------------------

If there is network access, geocodes can be looked up for a given
query using google's geocode lookup API.  This is all done behind the
scenes for you using a ``GeocodeQuery`` object.

  >>> geoQuery = geocode.GeocodeQuery(u'LAX')
  >>> verifyObject(interfaces.IGeocodeQuery, geoQuery)
  True
  >>> geoQuery
  GeocodeQuery(u'LAX')
  >>> geoQuery.query
  u'LAX'

To perform the actual lookup, we actually do an adaptation from
IGeocodeQuery to IGeocode.  First we must register the adapter (done
for you in zcml),

  >>> import zope.component
  >>> zope.component.provideAdapter(geocode.getGeocodeFromQuery)
  >>> try:
  ...     geo = interfaces.IGeocode(geoQuery)
  ... except IOError, e:
  ...     geo = geocode.Geocode(33.944066, -118.408294)
  >>> geo
  Geocode(33.944066, -118.408294)

Managing Google Map API Keys
----------------------------

Google requires that all users of the google maps API provide an API
key for each base url that uses google maps.  For example, all
pages under ``http://subdomain.domain.com`` would use the API key that
corresponds to ``subdomain.domain.com``.  Maps under
``http://www.domain.com`` must use a separate API key.

API keys are managed and looked up as named utilities that implement
IGoogleMapAPIKey.

  >>> from keas.googlemap import apikey
  >>> LocalhostAPIKey = apikey.APIKey("ABQIAAAA8SpDMoY3XpgN5DzYnmNsmhTwM0brOpm-All5BF6PoaKBxRWWERT3cHSc49vCxDS6hLf1VMPD_e-ekg")
  >>> LocalhostAPIKey
  APIKey('ABQIAAAA8SpDMoY3XpgN5DzYnmNsmhTwM0brOpm-All5BF6PoaKBxRWWERT3cHSc49vCxDS6hLf1VMPD_e-ekg')

  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(interfaces.IGoogleMapAPIKey, LocalhostAPIKey)
  True

Now we can register the ``LocalhostAPIKey`` component as a named
utility where the name is just the domain corresponding to the api
key.

  >>> zope.component.provideUtility(LocalhostAPIKey,
  ...                               interfaces.IGoogleMapAPIKey,
  ...                               'localhost')

When registering this utility in zcml, you would do something like this::

  <utility
      provides="keas.googlemap.interfaces.IGoogleMapAPIKey"
      component="app.package.module.LocalhostAPIKey"
      name="localhost"
      />

Now we can query for the utitlity to get the api key based on the
domain name.

  >>> zope.component.queryUtility(interfaces.IGoogleMapAPIKey, 'localhost').key
  'ABQIAAAA8SpDMoY3XpgN5DzYnmNsmhTwM0brOpm-All5BF6PoaKBxRWWERT3cHSc49vCxDS6hLf1VMPD_e-ekg'

This shows you how you would add your own api keys for your own
domains.  However, since localhost is the most common domain name used
during development, we already provide the api key for the localhost
domain in the ``keas.googlemap`` package.  The utitlity registration
for this api key can be included in your application with a zcml
include like so::

  <include package="keas.googlemap" file="apikey.zcml" />

The actual ``APIKey`` component is located here:

  >>> apikey.LocalhostAPIKey
  APIKey('ABQIAAAA8SpDMoY3XpgN5DzYnmNsmhTwM0brOpm-All5BF6PoaKBxRWWERT3cHSc49vCxDS6hLf1VMPD_e-ekg')


JavaScript Viewlet for Loading Google Maps API
----------------------------------------------

Any page that has a google map on it must include Google's javascript
code.  This means putting a script tag in your page that looks like this::

  <script type="text/javascript"
          src="http://maps.google.com/maps?file=api&v=2&key=some_really_long_api_key">
  </script>

As you can see, the ``src`` attribute references the API key which
must be dynamically generated based on the domain name under which the
page is displayed.  We can satisfy this requirement using a viewlet
that performs the API key lookup at render time.

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> request.getURL = lambda: 'http://localhost:8080' #monkey patching
  >>> viewlet = apikey.APIKeyViewlet('context', request, 'view', 'manager')
  >>> viewlet.update()
  >>> print viewlet.render()
  <script type="text/javascript"
          src="http://maps.google.com/maps?file=api&v=2&key=ABQIAAAA8SpDMoY3XpgN5DzYnmNsmhTwM0brOpm-All5BF6PoaKBxRWWERT3cHSc49vCxDS6hLf1VMPD_e-ekg&async=2&callback=keas_googlemap_maploader">
  </script>

If our request is under a host for which no apikey can be found, then
the viewlet silently fails passing back an html comment.

  >>> request = TestRequest()
  >>> request.getURL = lambda: 'http://someothersite.com/foo/bar/' #monkey patching
  >>> viewlet = apikey.APIKeyViewlet('context', request, 'view', 'manager')
  >>> viewlet.update()
  >>> print viewlet.render()
  <!-- Google Maps API Key not found for someothersite.com -->

Here is how the viewlet registration would look in ZCML::

  <viewlet
      name="googleMapsAPIKey"
      manager="your.viewlet.manager.IJavaScript"
      class="keas.googlemap.apikey.APIKeyViewlet"
      permission="zope.Public"
      layer="your.browser.layer.IYourBrowserLayer"
      />


Connecting Geocodes to Objects
------------------------------

Your application will probably have some object that maps to a
geocode, like an address object.  So lets create one to play with.

  >>> import zope.interface
  >>> import zope.schema
  >>> class IAddress(zope.interface.Interface):
  ...    street = zope.schema.TextLine(title=u"street")
  ...    city = zope.schema.TextLine(title=u"city")
  ...    state = zope.schema.TextLine(title=u"state")
  ...    zipcode = zope.schema.TextLine(title=u"zipcode")

  >>> class Address(object):
  ...    zope.interface.implements(IAddress)
  ...    def __init__(self, **kwargs):
  ...        for key, arg in kwargs.items():
  ...            setattr(self, key, arg)

Now we can create a new address object.

  >>> zopecorp = Address(street=u"513 Prince Edward Street",
  ...                    city=u"Fredericksberg",
  ...                    state=u"VA",
  ...                    zipcode=u"22401")

To obtain the geocode to be associated with this object, we must
query the google map service.  The latitude and longitude data
is encapsulated within the IGeocode interface.

  >>> from keas.googlemap import geocode
  >>> geo = geocode.Geocode(37.790024, -122.397831)
  >>> verifyObject(interfaces.IGeocode, geo)
  True
  >>> print geo
  Geocode(37.790024, -122.397831)

If localhost has network access, then geocode data can be accessed
dynamically.

  >>> # the below makes tests not fail when there is no network access.
  >>> try:
  ...   geo = geocode.getGeocodeFromAddr(
  ...     zopecorp.street, zopecorp.city,
  ...     zopecorp.state, zopecorp.zipcode)
  ... except IOError, e:
  ...   geo = geocode.Geocode(38.29793, -77.459799)
  >>> print geo
  Geocode(38.2..., -77.4...)


Annotating Objects with Geocodes
--------------------------------

Objects can be annotated with a geocode.  The object must only
implement the ``IHaveGeocode`` interface to have a geocode.

  >>> import zope.interface
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> class Building(object):
  ...     zope.interface.implements(interfaces.IHaveGeocode,
  ...                               IAttributeAnnotatable)

The geocode annotation is accessed via an adapter that is registered
for the ``IHaveGeocode`` interface.

  >>> keasOffice = Building()
  >>> keasGeo = interfaces.IGeocode(keasOffice)
  >>> keasGeo
  Geocode(0.0, 0.0)
  >>> keasGeo.latitude = 3.4
  >>> keasGeo.longitude = 5.6
  >>> interfaces.IGeocode(keasOffice)
  Geocode(3.4, 5.6)

The geocodes are stored as annotations on any object, which is then
adapted to IGeocode to retrieve the geocode info. Here is a simplistic
class diagram::

  Building:
    implements(IHaveGeocode)
    implements(IAttributeAnnotatable)

  geocode.getGeocodeAnnotation:
    IAttributeAnnotatable -(adapts)-> IGeocode


Grouping and Sorting Geocodes
-----------------------------

Any objects that can be adapted to IGeocode can be grouped together in
a single ``CenteredGeocodes`` object. Let's create such a collection.

  >>> keasOffice = Building()
  >>> starbucks = Building()
  >>> starbucks2 = Building()
  >>> starbucks3 = Building()

  >>> interfaces.IGeocode(keasOffice).update(37.790024, -122.397832)
  >>> interfaces.IGeocode(starbucks).update(37.791355, -122.398801)
  >>> interfaces.IGeocode(starbucks2).update(37.791687, -122.398381)
  >>> interfaces.IGeocode(starbucks3).update(40.711761, -74.006676)

  >>> codes = [starbucks2,
  ...          starbucks,
  ...          starbucks3]
  >>> centered = geocode.CenteredGeocodes(keasOffice, *codes)
  >>> verifyObject(interfaces.ICenteredGeocodes, centered)
  True

The geocodes are stored as a list of distance, geocode pairs.  Since
different computers have different floating point capabilities, we
will just do this to centimeter precision.

  >>> import pprint
  >>> pprint.pprint([(int(d*100000),interfaces.IGeocode(g)) for d, g in centered])
  [(17079,     Geocode(37.791355, -122.398801)),
   (19116,     Geocode(37.791687, -122.398381)),
   (412785883, Geocode(40.711761, -74.006676))]


