Google Map Browser Pages
========================

keas.googlemap provides minimal functionality for defining a google
map through python constructs and generating the proper javascript for
creating such a google map via the gmaps API.


Defining a Google Map
---------------------

Let's start by creating a map definition using the ``GoogleMap`` class.

  >>> from keas.googlemap import browser
  >>> from keas.googlemap.browser import interfaces

  >>> gmap = browser.GoogleMap()
  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(interfaces.IGoogleMap, gmap)
  True

By default, the map has the following attributes:

  >>> gmap.id
  u'google-map'
  >>> gmap.zoom
  1
  >>> gmap.type
  u'G_NORMAL_MAP'

A quick note about the google map types.  There are three types known
to this API, and they are stored in the following global variables.

  >>> interfaces.NORMAL_MAP
  u'G_NORMAL_MAP'
  >>> interfaces.SATELLITE_MAP
  u'G_SATELLITE_MAP'
  >>> interfaces.HYBRID_MAP
  u'G_HYBRID_MAP'

  >>> gmap.width
  500
  >>> gmap.height
  400
  >>> gmap.markers
  []

Let's try rendering the javascript needed to create such a map.

  >>> print gmap.render()
  <div style="width: 500px; height: 400px" id="google-map">
  [Google Map - If you see this, your browser is not compatible with
  google maps, or there was an error.]
  </div>
  <BLANKLINE>
  <script type="text/javascript">
            $(document).ready( function() {
                 keas.googlemap.initialize({id:'google-map',
                                            zoom:1,
                                            type:G_NORMAL_MAP,
                                            markers:[]});} );
            $(document).unload( function() {GUnload();} );
            </script>
  <BLANKLINE>

Adding Markers
--------------

  >>> markerHTML = u"""
  ... <h1>My Marker</h1>
  ... <p>This is my marker</p>
  ... """
  >>> from keas.googlemap import geocode
  >>> marker = browser.Marker(geocode=geocode.Geocode(37.231,-23.123),
  ...                         html=markerHTML)
  >>> marker
  Marker(Geocode(37.231, -23.123), u'\n<h1>My Marker</h1>\n<p>This is my marker</p>\n')

Now we will add this marker to the map and render it again.

  >>> gmap.markers.append(marker)
  >>> print gmap.render()
  <div style="width: 500px; height: 400px" id="google-map">
  [Google Map - If you see this, your browser is not compatible with
  google maps, or there was an error.]
  </div>
  <BLANKLINE>
  <script type="text/javascript">
            $(document).ready( function() {
                 keas.googlemap.initialize({id:'google-map',
                                            zoom:1,
                                            type:G_NORMAL_MAP,
                                            markers:[{latitude:37.231, longitude:-23.123, html:'\n<h1>My Marker</h1>\n<p>This is my marker</p>\n'},]});} );
            $(document).unload( function() {GUnload();} );
            </script>
  <BLANKLINE>
