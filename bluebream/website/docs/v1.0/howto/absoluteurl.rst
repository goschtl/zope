Retrieving absolute URL for an object
=====================================

.. based on http://zope-cookbook.org

BlueBream has a different, cleaner approach on how to handle URLs of
objects.  This recipe presents how to retrieve an URL for a given
object, and the logic behind.  This HOWTO assume that you have
included ``zope.traversing.browser`` in your ``etc/site.zcml`` like
this::

  <include package="zope.traversing.browser" />

Understanding URLs
------------------

Each persistent object stored in the ZODB is reached through views,
that handles its display.  The URL is the location from wich the
object is reached through the browser.  For example, is the user
tries to display foo , which is in bar , she will type:
``http://server/foo/bar``.  The object is pulled by the publisher
which traverses the tree of objects from the root.  In our case, it
traverses foo , ask it for bar , and so on.  foo will point bar to
the publisher, because its ``__name__`` property is bar .

Getting an object URL is done by doing the back trip from the object
to the root, building the string with the names of all traversed
objects.

The main difference with older behaviors is that bar doesn't hold its
URL.

Getting an object URL
---------------------

The URL of all publishable objects can be retrieved this way, and a
generic view class, called ``AbsoluteURL`` provide this feature under
the ``absolute_url`` name.

In a ZPT for instance, a given object URL can be retrieved with:
``my_object/@@absolute_url``.  In Python code, a call to the
``zope.traversing.browser.absoluteurl.absoluteURL`` function can be
used.

To try this function, open the debug shell::

  $ ./bin/paster shell debug.ini

You can retrieve the root object URL, like this:

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.traversing.browser.absoluteurl import absoluteURL
  >>> request = TestRequest()
  >>> absoluteURL(root, request)
  'http://127.0.0.1'

In the above example, ``root`` is the root folder object.
