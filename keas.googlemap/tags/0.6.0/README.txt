=============================
Zope 3 Google Map Integration
=============================

.. contents::

Introduction
------------

The ``keas.googlemap`` package provides an easy way to bring google
maps into your zope 3 applications.  Some of the features of
``keas.googlemap`` are:

  - Look up geocodes (latitude and longitude coordinates) for any
    query string

  - Manage Google Map API keys for multiple domains

  - Sort geocodes by distance using the haversine function

  - Python representation of a google map that will render all the
    necessary javascript to display the map, including geocode
    markers.

Demo
----

See for yourself what ``keas.googlemap`` is capable of by running the
demo.  To run the demo, type the following commands:

Download the source from the Zope subversion repository::

 $ svn co svn://svn.zope.org/repos/main/keas.googlemap/trunk keas.googlemap
 $ cd keas.googlemap

Run the ``bootstrap.py`` and ``buildout`` scripts::

  $ python bootstrap.py
  $ ./bin/buildout

Start the demo server::

  $ ./bin/demo fg

You should now be able to go http://localhost:8080 and see a google map
with options for how the google map should be displayed.

Live Demo
---------

If you are too lazy to try out the demo yourself, you can also see it
running at http://demo.carduner.net/keas.googlemap/