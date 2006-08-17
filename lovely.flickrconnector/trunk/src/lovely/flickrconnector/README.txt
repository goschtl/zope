================
Flickr Connector
================

This package integrates the functionality of the generic python
``lovely.flickr`` package to Zope 3 by providing a utility:

  >>> from lovely import flickrconnector
  >>> connector = flickrconnector.FlickrConnector()
  
As you know we need an api_key and a shared secret to use the Flickr API:

  >>> connector.api_key = u'a8d135acf227a6c9471c5b6d24877080'
  >>> connector.shared_secret = u'cf4c77be4d206e6a'

The Connector provides all Flickr functions:

  >>> result = connector.test.echo(foo='bar')
  >>> result['api_key']
  'a8d135acf227a6c9471c5b6d24877080'
  >>> result['method']
  'flickr.test.echo'
  >>> result['foo']
  'bar'

See ``lovely.flickr`` package for the full documentation of the API
