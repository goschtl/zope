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
  >>> gmap.controls
  ['GLargeMapControl', 'GMapTypeControl']

A quick note about the google map types.  There are three types known
to this API, and they are stored in the following global variables.

  >>> interfaces.NORMAL_MAP
  u'G_NORMAL_MAP'
  >>> interfaces.SATELLITE_MAP
  u'G_SATELLITE_MAP'
  >>> interfaces.HYBRID_MAP
  u'G_HYBRID_MAP'

There are also several different typs of controls that can be
displayed on a map.

  >>> interfaces.GLargeMapControl
  'GLargeMapControl'
  >>> interfaces.GSmallMapControl
  'GSmallMapControl'
  >>> interfaces.GSmallZoomControl
  'GSmallZoomControl'
  >>> interfaces.GScaleControl
  'GScaleControl'
  >>> interfaces.GMapTypeControl
  'GMapTypeControl'
  >>> interfaces.GHierarchicalMapTypeControl
  'GHierarchicalMapTypeControl'
  >>> interfaces.GOverviewMapControl
  'GOverviewMapControl'

  >>> gmap.width
  500
  >>> gmap.height
  400
  >>> gmap.markers
  []

Let's try rendering the javascript needed to create such a map.

  >>> print gmap.render()
  <div style="width: 500px; height: 400px" id="google-map">
  Loading Map...
  </div>
  <BLANKLINE>
  <script type="text/javascript">
            var keas_googlemap_maploader = function(){
                 keas.googlemap.initialize({id:'google-map',
                                            zoom:1,
                                            type:G_NORMAL_MAP,
                                            controls:["GLargeMapControl", "GMapTypeControl"],
                                            popup_marker:null,
                                            markers:[]});
            };
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
  Loading Map...
  </div>
  <BLANKLINE>
  <script type="text/javascript">
            var keas_googlemap_maploader = function(){
                 keas.googlemap.initialize({id:'google-map',
                                            zoom:1,
                                            type:G_NORMAL_MAP,
                                            controls:["GLargeMapControl", "GMapTypeControl"],
                                            popup_marker:null,
                                            markers:[{"latitude": 37.2..., "html": "\n<h1>My Marker</h1>\n<p>This is my marker</p>\n", "longitude": -23.1...}]});
            };
            $(document).unload( function() {GUnload();} );
            </script>
  <BLANKLINE>

By default, marker's popup appears when marker is clicked, but we can change it to
get popup apper on page load. Note that with Google maps, only one popup can be
visible at the same time.

  >>> marker.popupOnLoad = True
  >>> print gmap.render()
  <div style="width: 500px; height: 400px" id="google-map">
  Loading Map...
  </div>
  <BLANKLINE>
  <script type="text/javascript">
            var keas_googlemap_maploader = function(){
                 keas.googlemap.initialize({id:'google-map',
                                            zoom:1,
                                            type:G_NORMAL_MAP,
                                            controls:["GLargeMapControl", "GMapTypeControl"],
                                            popup_marker:0,
                                            markers:[{"latitude": 37.2..., "html": "\n<h1>My Marker</h1>\n<p>This is my marker</p>\n", "longitude": -23.1...}]});
            };
            $(document).unload( function() {GUnload();} );
            </script>
  <BLANKLINE>

If we'll try to add one more marker with popupOnLoad == True, the map's ``render``
method will raise a ValueError:

  >>> marker = browser.Marker(geocode=geocode.Geocode(37.231,-23.123),
  ...                         html=u'Test',
  ...                         popupOnLoad=True)

  >>> gmap.markers.append(marker)
  >>> print gmap.render()
  Traceback (most recent call last):
  ...
  ValueError: Only one marker can have popup on load at the same time

To properly display markers, you will need to include the
markermanager.js utility script from google.  There is a viewlet that
renders the appropriate script tag.

  >>> print browser.GoogleMapMarkersViewlet('context','request','view','manager').render()
  <script
    type="text/javascript"
    src="http://gmaps-utility-library.googlecode.com/svn/trunk/markermanager/release/src/markermanager.js"></script>
