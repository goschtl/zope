======
Flickr
======

Flickr holds millions of photos and provides a rich and powerful API. The API
definition can be found at 'http://www.flickr.com/services/api/'

this modules follows pretty strictly the API.

  >>> from lovely import flickr

the main areas are:

auth, blogs, contacts, favorites, groups, interestingness, people, photos,
photosets, reflection, tags, test, urls

To use the Flickr API you need to have an application key. Flickr uses this
key to track API usage.
This is Lovely Systems non-commercial key for development:

  >>> API_KEY=u'a8d135acf227a6c9471c5b6d24877080'
  >>> SHARED_SECRET=u'cf4c77be4d206e6a'


If the connection to flickr results in an error, a FlickrError is beeing
raised.

  >>> flickr.test.echo(api_key=u'bullshit')
  Traceback (most recent call last):
  ...
  FlickrError: Flickr Error 100: Invalid API Key (Key not found)

